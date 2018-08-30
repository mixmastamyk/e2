

docs: test_quiet
	rst2html.py readme.rst > readme.html


test:
	python3 env.py -v; echo status: $$?


test_quiet:
	@python3 env.py; echo status: $$?



publish: test
	python3 setup.py sdist upload


clean:
	git gc
	rm -rf readme.html build dist

	-find -type d -name __pycache__ -exec rm -rf '{}' \;



# always do it, having trouble where half the time it doesn't work :(
.PHONY: docs test publish clean
