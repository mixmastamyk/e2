

test:
	python3 env.py -v; echo status: $$?


test_quiet:
	@python3 env.py; echo status: $$?


publish: test
	rm -rf build  # possible wheel bug
	python3 setup.py sdist bdist_wheel --universal upload


readme.html: test_quiet
	rst2html.py readme.rst > readme.html
	refresh.sh Firefox


clean:
	git gc
	rm -rf readme.html build dist MANIFEST *.pyc

	-find -type d -name __pycache__ -exec rm -rf '{}' \;



# all targets for now
.PHONY: $(MAKECMDGOALS)
