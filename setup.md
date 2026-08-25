# Setup

You will need the following tools for this class: **R**, **Positron**, **Git**, a **C++ compiler**, and later **Python**.

---

## Before you start: check your hardware

You should check the following before you start:

- **Mac**: open Terminal and run `uname -m`, and then `sw_vers`.
- **Windows**: open PowerShell and run `echo $env:PROCESSOR_ARCHITECTURE`.

Please note that **an Intel Mac** (`x86_64`) or **a Windows ARM laptop** (`ARM64`) cannot run PyTorch, which we need from the deep learning lecture onward. Everything else in the course should be fine. If you have issues with PyTorch, please reach out sooner rather than later and we will make a plan.

**Apple Silicon Macs below macOS 14** cannot run the current version of R, so you will need to update your macOS. Intel Macs are fine from macOS 11 up.

---

## Install in this order

The order matters. Two of these steps are invisible if you skip them, and you find out weeks later.

### 1. R

Download from [cloud.r-project.org](https://cloud.r-project.org/). Take the build that matches your machine — Apple Silicon Macs need the `arm64` package, not the Intel one.

Verify: `R --version` prints 4.6.1. Anything below 4.2 will not show up in Positron.

### 2. The compiler

We fit Bayesian models with Stan. Stan writes C++ and compiles it on your computer every time you fit a new model. R cannot do that by itself, so you install a compiler.

**macOS.** Run the following command in Terminal:

```
xcode-select --install
```

Click through the dialog. If you do not have Git installed this will also install it. 

**Windows.** You will need to install two things:

1. The [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe). Nothing enforces this and the failure it causes is unreadable.
2. [Rtools45](https://cran.r-project.org/bin/windows/Rtools/). Accept the default location and do not edit your PATH. Ignore any guide that tells you to set `BINPREF` — that advice is a decade old and now breaks things.

**Linux.** `sudo apt install build-essential libgdal-dev libgeos-dev libproj-dev libudunits2-dev`

### 3. Git

- **macOS**: Git will already be installed. Go straight to the config below. 
- **Windows**: [Git for Windows](https://git-scm.com/download/win). The installer asks about eleven questions and **exactly one default is wrong**: on "Adjusting the name of the initial branch", choose "Override the default branch name" and type `main`. Press Next through everything else.
- **Linux**: `sudo apt install git`

Then, once, in a terminal:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

Get a GitHub account if you do not have one. Authenticate with the [GitHub CLI](https://cli.github.com/): `gh auth login`. Do not fight with tokens.

### 4. Positron

Download the current release from [positron.posit.co/download.html](https://positron.posit.co/download.html). The page detects your machine.

**Install R first.** Positron does not install R and does not warn you. With no R, it opens and says it has no interpreter, which looks like Positron is broken. If you installed R while Positron was open, run `Interpreter: Discover All Interpreters` from the Command Palette.

**Windows**: if needed you can choose "user install", not "system install".

### 5. Do not install Quarto

**Positron already includes Quarto.** There are lots of Quarto tutorials online that open by telling you to download Quarto separately, because those tutorials were written for RStudio. If you install Positron you should not need a separate Quarto install.

### 6. R packages

In the Positron R console:

```r
install.packages(c(
  "tidyverse", "glmnet", "ranger", "xgboost",
  "rstan", "rstanarm", "brms",
  "sf", "terra",
  "pkgbuild"
))
```

These install as prebuilt binaries. You still need the compiler from step 2. Stan compiles C++ every time you fit a model.

Do not install `cmdstanr`. Every brms tutorial recommends it. It is not on CRAN, the build takes twenty minutes and several GB, and `brms` uses the `rstan` backend by default, which is what we want.

### 7. Python — not yet

We do not touch Python until the deep learning lecture. Positron can install it for you when we get there, so leave it. I will circulate instructions in October.

---

## Check that it works

Run these and send me the output before the first section.

In a terminal:

```
R --version
git --version
gh auth status
```

In the Positron R console:

```r
# Compiler present? This must print TRUE.
pkgbuild::has_build_tools(debug = TRUE)

# Packages load?
library(tidyverse); library(sf); library(glmnet)

# The real test: does Stan compile and sample?
fit <- brms::brm(mpg ~ wt, data = mtcars, chains = 1, iter = 500)
```

That last one is slow the first time, because it is compiling. Slow is fine. An error is not.

In Positron, visually: open a new `.qmd`, put one R chunk in it, click Render, and see output. Check that the Source Control panel offers to initialize a repository.

---

## When something breaks

Positron's Command Palette has `Runtime Startup Diagnostics`, which is the right first move when the console will not start. `Developer: Reload Window` fixes a surprising amount and does not lose your session.

If you are stuck for more than twenty minutes, stop and post an issue on the GitHub repo.
