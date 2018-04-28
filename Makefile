
# always do it, having trouble where half the time it doesn't work :(
.PHONY: readme.html test


readme.html: test_quiet
	rst2html.py readme.rst > readme.html


test:
	python3 env.py -v; echo status: $$?


test_quiet:
	@python3 env.py; echo status: $$?

