test:
	python3 -m unittest discover -s tests -v

build:
	python3 -m compileall -q coursecolumns tests

demo:
	python3 -m coursecolumns
