
.PHONY: clean
clean:
	rm -rf build dist hexalate.egg-info

.PHONY: install

install:
	python setup.py install

.PHONY: uninstall

uninstall:
	pip uninstall hexalate