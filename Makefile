
# always do it, having trouble where half the time it doesn't work :(
.PHONY: docs test


test:
	python3 env.py -v; echo status: $$?


test_quiet:
	@python3 env.py; echo status: $$?


docs: test_quiet
	rst2html.py readme.rst > readme.html
