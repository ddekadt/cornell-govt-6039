"""Write section10.qmd (student version) from section10_instructor.qmd: drop the answer blocks."""
import re
s = open("section10_instructor.qmd").read()
s = s.replace(" | Instructor version", "").replace("solutions: true", "solutions: false")
out, skip = [], False
for line in s.split("\n"):
    if not skip and re.match(r"^::: (sol|\{\.sol)", line):
        skip = True
        continue
    if skip:
        if line.strip() == ":::":
            skip = False
        continue
    out.append(line)
s = "\n".join(out)
s = re.sub(r"\n{3,}", "\n\n", s)
open("section10.qmd", "w").write(s)
