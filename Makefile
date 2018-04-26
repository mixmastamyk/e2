
# always do it, having trouble where half the time it doesn't work :(
.PHONY: readme.html

readme.html:
	rst2html.py readme.rst > readme.html

