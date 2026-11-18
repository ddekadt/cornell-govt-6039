# Generated from section10.ipynb: the notebook is easier to read; open it in Google Colab or Jupyter.


# # Borrowing a deep network: the code, step by step
#
# *GOVT 6039, Section 10. Companion to Lectures 18 and 19.*
#
# In Lectures 18 and 19 we built neural networks ourselves: first a small one in `nnet` on six features of polling stations, then a wider one in PyTorch on pixels of handwritten digits. Both were trained from scratch on our own labelled data. The digit network needed 21,844 labelled examples to reach 72% accuracy.
#
# Text is harder than digits, and a political scientist rarely has twenty thousand coded sentences. The usual way out is to **borrow** a network that someone else has already trained on enormous amounts of text, and use what it has learned. This notebook walks through that, with real parliamentary speech, in the same notation as the lectures. You can run every step yourself.
#
# **The question.** Can a network trained by someone else measure the *tone* of what MPs say in parliament: whether a sentence praises, thanks, criticises or attacks? And when should we trust its numbers?


# ## The data: ParlaSent
#
# ParlaSent (Mochtak, Rupnik and Ljubešić 2023) is a set of sentences taken from parliamentary debates in Bosnia and Herzegovina, Croatia, Serbia, Czechia, Slovakia, Slovenia and the United Kingdom. Trained annotators read each sentence and coded its tone on a six-point scale, which we turn into numbers from 0 to 5:
#
# - 0 = Negative
# - 1 = Mostly negative
# - 2 = Neutral, leaning negative
# - 3 = Neutral, leaning positive
# - 4 = Mostly positive
# - 5 = Positive
#
# The data come in seven files of 2,600 sentences each:
#
# - **Five training files** (one each for Bosnian/Croatian/Serbian, Czech, Slovak, Slovenian and English). Two annotators coded every sentence independently, then agreed on a final code. These are the sentences the network was trained on.
# - **Two test files** (Bosnian/Croatian/Serbian, and English). One annotator coded each sentence. The network has **never seen** these, so they are where we can check it honestly.
#
# Besides the sentence and its code, each row records who said it: the MP's `name`, `party`, `gender`, the `date`, and `ruling`, which is meant to say whether the MP's party was in government ("Coalition") or in opposition. (Part 5 shows that this last column is not quite what it seems.)
#
# The data are free to use and share under a CC BY-SA 4.0 licence. We use four of the files: the English training file, the two test files, and the Czech training file.


# ## The two networks
#
# Both start from **XLM-R**, a network with 24 layers and about 560 million weights, trained by Facebook AI on text in 100 languages. Its training task was simple: hide some words in a sentence and predict them. To get good at that across languages, the network had to learn a great deal about what sentences mean. The ParlaMint project then continued that training on 1.72 billion words of speeches from 26 European parliaments.
#
# - **Network A** (`classla/xlm-r-parlasent`) was then trained once more, on the ParlaSent training sentences and their codes, to output a tone score from 0 to 5. This is the network we borrow in Parts 1 to 3 and 5.
# - **Network B** (`classla/xlm-r-parla`) stopped before that last step. It has never seen a single tone code. We use it in Part 4, to play the role of a general-purpose network borrowed for a new task.


# ## How to run this notebook
#
# **The easiest way is Google Colab**, which runs Python in your browser for free:
#
# 1. Go to [colab.research.google.com](https://colab.research.google.com) and choose *File > Upload notebook*, then pick this file (`section10.ipynb`).
# 2. Choose *Runtime > Change runtime type > T4 GPU*. A GPU makes the networks about 50 times faster. It is free.
# 3. Run the cells from top to bottom: click into a cell and press **Shift + Enter**.
#
# **On your own laptop** you need Python 3.10 or newer and Jupyter (for example through VS Code or Anaconda). Run the cells in the same order. A laptop processor scores about five sentences a second, so the code uses samples of a few hundred sentences: each step takes a minute or two.
#
# The first time you load a network, it is downloaded from huggingface.co (about 2.2 GB each). After that it is stored on your computer (or in your Colab session) and loads in seconds.


# ## Python in two minutes
#
# If you have only used R, here is what you need to read the code below.
#
# - **Cells.** The notebook is a list of cells. Text cells (like this one) explain; code cells run. Run them in order: later cells use what earlier cells created.
# - **Comments.** Anything after `#` on a line is a comment for you; Python ignores it.
# - **Assignment.** `x = 5` stores 5 under the name `x` (R's `x <- 5`).
# - **Libraries.** `import pandas as pd` loads a library and gives it a short name. Then `pd.read_json(...)` means "the function `read_json` from pandas".
# - **Data frames.** pandas data frames work like R's. `df["party"]` is a column; `df.head()` shows the first rows; `df[df["y"] == 5]` keeps the rows with code 5.
# - **Functions.** `def name(arguments):` starts a function; the indented lines below it are its body, and `return` gives back the result (R's `function(...) { ... }`).
# - **Indentation matters.** Python uses indentation instead of `{ }` to mark what belongs inside a function, a loop or an `if`.


# ## Step 0: Install, load the libraries and look at the data
#
# The first cell installs the libraries. In Colab most of them are already there, so this is quick; on a laptop it may take a few minutes the first time. If you run this on your own computer and have already installed them, you can skip it.

# The "!" runs a command in the terminal rather than in Python.
# !pip install -q torch transformers pandas numpy scikit-learn matplotlib   (run this in a terminal)


# Next we load the libraries. Each one does a specific job:
#
# - **numpy**: vectors and matrices, like R's matrix algebra;
# - **pandas**: data frames;
# - **torch** (PyTorch): the library the networks run in, the same one Lecture 19 used for the digit network;
# - **transformers**: downloads pretrained networks by name and prepares text for them;
# - **matplotlib**: plots.

import os, urllib.request              # for downloading the data files
import numpy as np                     # vectors and matrices
import pandas as pd                    # data frames
import torch                           # the library the networks run in
import matplotlib.pyplot as plt        # plots
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

torch.set_grad_enabled(False)          # we only use the networks, never train them: no slopes needed
print("torch", torch.__version__, "| GPU available:", torch.cuda.is_available())


# Now the data. The function `read()` below finds a ParlaSent file in the folder `data/raw/` (where it sits if you cloned the course repo), or else downloads it once from the course repo. It turns the six text labels into the numbers 0 to 5 and stores them in a column `y`.
#
# One detail: in the training files the final code is in the column `reconciliation` (the code the two annotators agreed on); in the test files, which only one annotator coded, it is in `annotator1`.

REPO = "https://raw.githubusercontent.com/ddekadt/cornell-govt-6039/main/sections/section10/data/raw/"

# A dictionary: each text label -> its number on the 0-5 scale.
scale = {"Negative": 0, "M_Negative": 1, "N_Neutral": 2,
         "P_Neutral": 3, "M_Positive": 4, "Positive": 5}

def read(name):
    # Use the local copy if there is one; otherwise download the file once from the course repo.
    path = os.path.join("data", "raw", name)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        urllib.request.urlretrieve(REPO + name, path)
    d = pd.read_json(path, lines=True)                 # one sentence (one JSON record) per line
    column = "reconciliation" if "reconciliation" in d.columns else "annotator1"
    d["y"] = d[column].map(scale)                     # text label -> number
    return d

uk  = read("ParlaSent_EN_test.jsonl")      # 2,600 UK sentences the network never saw
bcs = read("ParlaSent_BCS_test.jsonl")     # 2,600 Bosnian, Croatian and Serbian sentences, same
print(len(uk), "UK sentences;", len(bcs), "BCS sentences")


# Always look at the data before modelling it. Here are a few UK sentences with their codes, the parliaments in the BCS file, and how often each code occurs.

pd.set_option("display.max_colwidth", 110)                  # show more of each sentence
print(uk[["sentence", "y", "party", "date"]].head(8))

print("\nSentences per parliament in the BCS file:")
print(bcs["country"].value_counts())

# How often is each code used? One bar per code, UK and BCS side by side.
counts = pd.DataFrame({"UK": uk["y"].value_counts(), "BCS": bcs["y"].value_counts()}).sort_index()
counts.plot.bar(figsize=(7, 3.5), rot=0, color=["#13946a", "#7a5cc9"])
plt.xlabel("code (0 = negative, 5 = positive)"); plt.ylabel("sentences"); plt.title("How the coders used the scale")
plt.gcf().set_facecolor("white"); plt.show()


# **What you should see.** Sentences of all kinds: thanks, attacks, procedure, statistics. The codes are spread over the whole scale, with many at the extremes (0 and 5) and at "neutral, leaning positive" (3). That spread is what the network has to reproduce.


# ## Step 1: One sentence through network A
#
# We load network A and its **tokenizer**. A network cannot read letters; the tokenizer cuts a sentence into *word pieces* (common words stay whole, rare words are split into parts) and replaces each piece by a number from a fixed vocabulary of 250,000 pieces. This is how one network can read 100 languages.
#
# The first time, this cell downloads about 2.2 GB, which can take a few minutes.

name = "classla/xlm-r-parlasent"                                  # network A
tok  = AutoTokenizer.from_pretrained(name)
net  = AutoModelForSequenceClassification.from_pretrained(name)
net.eval()                                                         # evaluation mode: dropout switched off (Lecture 19)

sentence = "I thank him for the leadership he has shown locally, and I encourage that."
enc = tok(sentence, return_tensors="pt")                           # "pt": give us PyTorch tensors
print(tok.convert_ids_to_tokens(enc["input_ids"][0]))              # the word pieces the network reads


# You should see the sentence in pieces, with `<s>` at the start and `</s>` at the end. The `▁` marks the start of a new word; *locally* became two pieces, `▁local` and `ly`.
#
# Now the **forward pass** (Lecture 19): the sentence goes through the network from left to right.
#
# 1. **Layers 1 to 24** turn every word piece into 1,024 numbers. Each layer builds its numbers from the layer before, as in Lecture 19's deep network. We keep the 1,024 numbers at the first piece, `<s>`: during training, the network learned to collect a summary of the whole sentence there. Call them $u(x)$, the **borrowed features**.
# 2. **Layer 25** is Lecture 18's hidden layer: $J = 1{,}024$ derived features, each a weighted mix of all the borrowed features, bent by an activation: $b_j(x) = \tanh\left(w_{j0} + \sum_k w_{jk} u_k(x)\right)$. The $\tanh$ is the sigmoid from Lecture 18, stretched to run from −1 to 1.
# 3. **The output** is a linear regression on the derived features: $\hat y = \beta_0 + \sum_j \beta_j b_j(x)$. A regression, not a class, because tone is a score.

h     = net.roberta(**enc).last_hidden_state        # layers 1-24: shape (1 sentence, 19 pieces, 1,024 numbers)
u     = h[:, 0, :]                                  # u(x): the 1,024 numbers at the first piece, <s>
b     = torch.tanh(net.classifier.dense(u))         # layer 25: the 1,024 derived features b_j(x)
y_hat = net.classifier.out_proj(b)                  # the output: beta_0 + sum_j beta_j b_j
print("shape of h:", tuple(h.shape))
print("network's y-hat:", round(y_hat.item(), 3))   # .item() turns a 1 x 1 tensor into a plain number


# The prediction should be about 5.4: clearly positive, and in fact above the top of the scale. Nothing keeps a regression inside 0 to 5.
#
# The last two layers are nothing more than the design matrix and regression of Lecture 18. To see that, we take their weights out of the network and redo the computation by hand with numpy. We should get exactly the same number.

W     = net.classifier.dense.weight.detach().numpy()                 # 1,024 x 1,024: the w_jk
w0    = net.classifier.dense.bias.detach().numpy()                   # 1,024: the intercepts w_j0
beta  = net.classifier.out_proj.weight.detach().numpy().ravel()      # 1,024: the beta_j
beta0 = net.classifier.out_proj.bias.detach().numpy()[0]             # 1 number: beta_0

u_vec = u.numpy().ravel()                                   # u(x) as a plain vector of 1,024 numbers
b_vec = np.tanh(w0 + W @ u_vec)                             # "@" is matrix multiplication (R's %*%)
print("y-hat by hand:", round(beta0 + beta @ b_vec, 3))

# How many weights? Lecture 18's formula (p + 1) J + J + 1 with p = J = 1,024:
print("weights in the last two layers:", W.size + w0.size + beta.size + 1)
print("weights in the whole network:  ", sum(p.numel() for p in net.parameters()))


# About a million weights in the last two layers and 560 million in all. Lecture 19 explains why such a network cannot be trained with `nnet`'s quasi-Newton steps: the curvature matrix would need one number for every *pair* of weights. It was trained with stochastic gradient descent on minibatches instead.
#
# **Try this.** Change `sentence` above to anything you like and rerun the three cells: a thank-you, an insult, a dry procedural sentence. Try a sentence in another language the network has read, such as German, French, Spanish or Russian. Can you find a sentence where it is clearly wrong?


# To score many sentences at once, we wrap these steps in a function. It feeds sentences through the network in **minibatches** of 16 (Lecture 19), which is much faster than one at a time, and returns two things: the matrix of borrowed features $u(x)$, one row per sentence, and the predictions $\hat y$.
#
# We score a random 300 sentences from each test file. On a laptop this takes a minute or two per file; on a Colab GPU a few seconds. With a GPU, feel free to raise `n` to 1,000 or all 2,600.

device = "cuda" if torch.cuda.is_available() else "cpu"    # use the GPU if there is one
net = net.to(device)

def run_network(sentences, batch_size=16):
    sentences = list(sentences)
    U, Y = [], []                                           # empty lists, filled one batch at a time
    for start in range(0, len(sentences), batch_size):      # start = 0, 16, 32, ...
        batch = sentences[start:start + batch_size]
        enc = tok(batch, padding=True, truncation=True, max_length=256, return_tensors="pt").to(device)
        u = net.roberta(**enc).last_hidden_state[:, 0, :]
        y = net.classifier.out_proj(torch.tanh(net.classifier.dense(u))).squeeze(-1)
        U.append(u.cpu().numpy()); Y.append(y.cpu().numpy())
        print(f"  {start + len(batch)} of {len(sentences)} sentences", end="\r")
    print()
    return np.vstack(U), np.concatenate(Y)                  # glue the batches together

n = 300
uk_s  = uk.sample(n, random_state=6039).reset_index(drop=True)    # random_state fixes the draw, like set.seed()
bcs_s = bcs.sample(n, random_state=6039).reset_index(drop=True)
U_uk,  uk_s["yhat"]  = run_network(uk_s["sentence"])
U_bcs, bcs_s["yhat"] = run_network(bcs_s["sentence"])
print(uk_s[["sentence", "y", "yhat"]].head(8))


# Each sentence now has the coder's code `y` and the network's `yhat` side by side. Scroll through and see where they agree and where they do not.


# ## Step 2: What the 24 layers learned
#
# Every sentence is now a point in a 1,024-dimensional space: its borrowed features $u(x)$. We cannot look at 1,024 dimensions, but we can find the two directions along which the sentences differ most and draw the sentences on those. These directions are called **principal components** (they are the topic of Lecture 20).
#
# If the network has learned something about tone, sentences with similar codes should land near each other. And since the network reads many languages, we can ask whether English and Croatian sentences end up in the same places.

from sklearn.decomposition import PCA

U_all = np.vstack([U_uk, U_bcs])                        # 600 x 1,024: both languages, stacked
codes = np.concatenate([uk_s["y"], bcs_s["y"]])         # their human codes
lang  = np.array(["UK"] * n + ["BCS"] * n)              # the language of each row

pca = PCA(n_components=2)
P = pca.fit_transform(U_all)                            # 600 x 2: each sentence's position on the map
print("share of all variation on axis 1 and axis 2:", pca.explained_variance_ratio_.round(2))
print("correlation of axis 1 with the human code:  ", np.corrcoef(P[:, 0], codes)[0, 1].round(2))

fig, ax = plt.subplots(1, 2, figsize=(11, 4.5), facecolor="white")
pts = ax[0].scatter(P[:, 0], P[:, 1], c=codes, cmap="coolwarm_r", s=12)   # red = negative, blue = positive
fig.colorbar(pts, ax=ax[0], label="human code")
ax[0].set_title("Coloured by the coder's code")
for l, colour in [("UK", "#13946a"), ("BCS", "#7a5cc9")]:
    ax[1].scatter(P[lang == l, 0], P[lang == l, 1], s=12, c=colour, label=l)
ax[1].set_title("Coloured by language"); ax[1].legend()
for a in ax: a.set_xlabel("axis 1"); a.set_ylabel("axis 2")
plt.show()


# **What you should see.** The first axis alone carries about half of all the variation in $u(x)$, and it is tone: it correlates with the human code at about ±0.8. (The sign of a principal component is arbitrary, so negative sentences may sit on the left or on the right.) The second axis separates the two languages. So **within each language, sentences line up by tone along the same axis**. That is why one output layer can read tone in English and in Croatian alike: its inputs are not words but positions in this shared space.


# ## Step 3: Is borrowing better than counting words?
#
# Without a borrowed network, a political scientist would fit a **bag of words**: one column per word, counting how often it appears in each sentence, and a ridge regression of the code on those counts, with the penalty chosen by cross-validation (Lecture 5). We train it on the 2,600 coded sentences of the English *training* file and test both models on the same test sentences as above.
#
# We measure accuracy with $R^2$ on the test sentences: the share of the variation in the coders' codes that the predictions account for. 1 is perfect; 0 is no better than predicting the average for everyone.

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score

train = read("ParlaSent_EN.jsonl")                       # 2,600 coded UK training sentences

# The bag of words: one column per word (letters only, any alphabet) used in at least 3 sentences.
vec     = CountVectorizer(token_pattern=r"(?u)[^\W\d_]+", min_df=3)
X_train = vec.fit_transform(train["sentence"])            # 2,600 sentences x about 2,400 words, mostly zeros
ridge   = RidgeCV(alphas=np.logspace(-2, 4, 30))          # sklearn calls the penalty lambda "alpha"
ridge.fit(X_train, train["y"])
print("words in the vocabulary:", X_train.shape[1])

uk_s["bow"]  = ridge.predict(vec.transform(uk_s["sentence"]))
bcs_s["bow"] = ridge.predict(vec.transform(bcs_s["sentence"]))
for label, d in [("UK ", uk_s), ("BCS", bcs_s)]:
    print(label, "R2: network", round(r2_score(d["y"], d["yhat"]), 2),
          "| bag of words", round(r2_score(d["y"], d["bow"]), 2))


# **What you should see.** On UK sentences the network reaches an $R^2$ of about 0.65 and the bag of words close to zero: a few hundred coded sentences are far too few for a word-count model. (Two trained coders, coding the same sentences independently, agree with an $R^2$ of about 0.65, so on this measure the borrowed network is as good as a second coder.) On the BCS sentences the network drops to about 0.5. That is a real loss, but the network keeps most of its signal in Bosnian, Croatian and Serbian, while the bag of words stays at zero.
#
# Why the collapse? The bag of words can only use words it saw in training, and those are English. Here is what it sees in a Serbian sentence:

s = "Neverovatno da je Vlada jedan ovakav zakon, koji je konfuzan i neprecizan, dala na usvajanje."
# ("Incredible that the Government put such a law, confusing and imprecise, up for adoption.")
words = vec.build_analyzer()(s)                           # split the sentence the same way as above
print("words the English vocabulary knows:", [w for w in words if w in vec.vocabulary_], "of", len(words))


# One word out of fifteen, and it is an accident of spelling: Serbian *i* means "and". With nothing to go on, the bag of words predicts roughly the same number for every non-English sentence.
#
# It is still worth seeing what the bag of words *did* learn. A ridge regression has one coefficient per word, so we can list the words that push a prediction up or down the most:

coef = pd.Series(ridge.coef_, index=vec.get_feature_names_out()).sort_values()
print("most negative words:", list(coef.index[:15]))
print("most positive words:", list(coef.index[-15:][::-1]))


# The lists make sense (*great*, *grateful*, *excellent*, *pleasure* against *concern*, *disappointed*, *dangerous*, *abuse*), but every word is a separate column, so the model knows nothing about a word it has not seen, and *disaster* and *catastrophe* share nothing. The network's features are learned from billions of words, in many languages.
#
# **Try this.** Print the sentences where the network is furthest from the coder: `uk_s.assign(err=uk_s.yhat - uk_s.y).sort_values("err")`. Would you have coded them the way the coder did?


# ## Step 4: Your own parliament, with few codes
#
# Now the situation you are more likely to face. You study a parliament and can afford to code, say, a hundred or a few hundred sentences yourself. How far does that get you?
#
# We use Czech, and network B. Why not network A? Network A was trained on the Czech training file, so testing it on Czech sentences would let it see the answers. Network B has the same 24 layers but has never seen a tone code, which is the honest stand-in for "a general network borrowed for a new task".
#
# We **freeze** network B: we do not change any of its weights, and only use the borrowed features $u(x)$ it produces. Then we fit a plain ridge regression of the code on those 1,024 features, using only the sentences we "coded". Because network B was never trained to put a summary at `<s>`, we take the average of its last layer over all the word pieces of the sentence instead.
#
# (If loading network B fails with a message about `torch.load`, run `!pip install -U torch` and restart.)

base = AutoModel.from_pretrained("classla/xlm-r-parla").to(device)   # network B, ~2.2 GB on first run
base.eval()

def features_B(sentences, batch_size=16):
    # u(x) from network B: the average of its last layer over each sentence's word pieces.
    sentences = list(sentences)
    U = []
    for start in range(0, len(sentences), batch_size):
        batch = sentences[start:start + batch_size]
        enc = tok(batch, padding=True, truncation=True, max_length=256, return_tensors="pt").to(device)
        h = base(**enc).last_hidden_state                      # sentences x word pieces x 1,024
        m = enc["attention_mask"].unsqueeze(-1)                # 1 for a real piece, 0 for padding
        U.append(((h * m).sum(1) / m.sum(1)).cpu().numpy())    # average over the real pieces only
        print(f"  {start + len(batch)} of {len(sentences)} sentences", end="\r")
    print()
    return np.vstack(U)

cz = read("ParlaSent_CZ.jsonl").sample(600, random_state=6039).reset_index(drop=True)
U_cz = features_B(cz["sentence"])                              # about 2 minutes on a laptop
test_cz, pool = cz.iloc[:300], cz.iloc[300:]                   # 300 sentences to test on; you "code" from the rest
U_test, U_pool = U_cz[:300], U_cz[300:]


# Now pretend you coded 25, 50, 100, 200 or 300 sentences. For each budget we fit two models on exactly those sentences and score them on the same 300 held-out sentences: ridge on network B's frozen features, and ridge on a bag of words built from the coded sentences.

alphas, results = np.logspace(-2, 4, 30), []
for n_codes in [25, 50, 100, 200, 300]:
    y_codes = pool["y"].values[:n_codes]
    frozen = RidgeCV(alphas=alphas).fit(U_pool[:n_codes], y_codes)                  # (a) borrowed features
    v = CountVectorizer(token_pattern=r"(?u)[^\W\d_]+", min_df=2)
    words = RidgeCV(alphas=alphas).fit(v.fit_transform(pool["sentence"].values[:n_codes]), y_codes)   # (b) words
    results.append({"codes": n_codes,
                    "frozen features": r2_score(test_cz["y"], frozen.predict(U_test)),
                    "bag of words": r2_score(test_cz["y"], words.predict(v.transform(test_cz["sentence"])))})
results = pd.DataFrame(results).set_index("codes")
print(results.round(2))

results.plot(marker="o", logx=True, figsize=(7, 4), color=["#2a78d6", "#e2622c"])
plt.axhline(0, color="grey", lw=0.8); plt.ylabel("test R2 on 300 Czech sentences"); plt.xlabel("sentences you coded")
plt.gcf().set_facecolor("white"); plt.show()


# **What you should see.** With a few dozen codes both models are poor. As the budget grows, the frozen features pull ahead, while the bag of words stays near zero: Czech has many forms of each word, so each form is its own column and appears once or twice. With our full data (1,000 coded sentences, see the section page) the frozen features reach an $R^2$ of about 0.35 and the bag of words about 0.03.
#
# But compare that with network A, whose weights were all trained on 13,000 coded sentences: it reaches about 0.6 on new sentences. The lesson: borrowed features beat counting words when codes are scarce, but **a network already trained for your task beats both**. Check whether one exists before you start coding.
#
# **Try this.** Your results will move from run to run because each budget uses one small random sample. Change `random_state` in the line that samples `cz` and rerun; how much do the numbers change?


# ## Step 5: Does the opposition sound more negative?
#
# A standing claim about parliaments is that opposition MPs speak more negatively than government MPs. The data record each speaker's status in the column `ruling`, so we can test it twice: once with the coders' codes, and once with the network's scores. If the network is a good measure, both should give the same answer.
#
# First, though, look at the covariate. In the UK, which party was in government?

uk_s["year"] = pd.to_datetime(uk_s["date"]).dt.year
print(pd.crosstab([uk_s["party"], uk_s["year"]], uk_s["ruling"]).loc[["Conservative", "Labour"]])


# The Conservatives governed throughout these years: with the Liberal Democrats until May 2015, and alone after that. Yet almost every Conservative sentence is labelled "Opposition". The column records whether the party was in a **coalition** government, so a single-party government counts as not ruling. Used as it is, it would compare the wrong groups, and nothing about the network's accuracy would warn us.
#
# So we recode government status from party and date, and drop the members of the House of Lords who belong to neither side.

date = pd.to_datetime(uk_s["date"])
uk_s["gov"] = ((uk_s["party"] == "Conservative") | ((uk_s["party"] == "Liberal Democrat") & (date < "2015-05-08"))).astype(float)   # 1.0 = government, 0.0 = opposition
uk_s.loc[uk_s["party"].isin(["Crossbench", "Bishops", "Non-affiliated"]), "gov"] = np.nan   # neither side

bcs_s["gov"] = (bcs_s["ruling"] == "Coalition").where(bcs_s["ruling"].notna())   # usable as coded here
both = pd.concat([uk_s, bcs_s]).dropna(subset=["gov"])
both["gov"] = both["gov"].astype(bool)

def gap(d, column):
    # opposition mean minus government mean, with a 95% interval
    a, b = d.loc[~d["gov"], column], d.loc[d["gov"], column]
    diff = a.mean() - b.mean()
    se = np.sqrt(a.var() / len(a) + b.var() / len(b))
    return f"{diff:+.2f} [{diff - 1.96 * se:+.2f}, {diff + 1.96 * se:+.2f}]"

for country, d in both.groupby("country"):
    print(f"{country:4s} n = {len(d):3d} | coders: {gap(d, 'y')} | network: {gap(d, 'yhat')}")


# **What you should see.** In the UK, Croatia and Serbia the opposition sounds more negative by both measures (negative gaps), and the network's gap is close to the coders'. With only 300 sentences per file the intervals are wide, and Bosnia and Herzegovina has too few sentences to say anything. On the section page, with 1,500 sentences per file, the network understates the Serbian gap by about a quarter.
#
# That is the general check for any borrowed measure: **the errors must be the same in the groups you compare**. An overall $R^2$ cannot tell you that; only coded sentences from each group can.


# ## What you did
#
# - You ran a 24-layer network and saw that its last two layers are Lecture 18's network, with $p = J = 1{,}024$.
# - You saw that its 1,024 borrowed features place sentences by tone, in two languages at once.
# - You compared it with the bag of words, in English and in a language the bag of words had never seen.
# - You saw how far a few hundred of your own codes get you with frozen features, and why a network trained for your task does better.
# - You checked a covariate before using it, and checked the measure on the comparison you care about.
#
# **Where to go from here.** The same steps work on any text you have: speeches, manifestos, tweets, open survey answers. Search [huggingface.co/models](https://huggingface.co/models) for a network already trained on a task close to yours, score a few hundred of your own coded examples to check it, and only then trust its numbers.
#
# *Data: Mochtak, Rupnik and Ljubešić (2023), ParlaSent 1.0, CLARIN.SI, CC BY-SA 4.0. Networks: classla/xlm-r-parlasent and classla/xlm-r-parla (Apache 2.0); Mochtak, Rupnik, Kuzman and Ljubešić (2025), Political Research Exchange; Conneau et al. (2020).*
