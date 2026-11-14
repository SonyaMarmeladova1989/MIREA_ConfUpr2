.PHONY: install test lint run clean

install:
	pip install -r requirements.txt

test:
	python -m pytest tests -v

lint:
	python -m py_compile src/*.py

run:
	python -m src.main --package $(PKG) --repo-url $(URL) \
		--mode $(MODE) --ascii-tree

clean:
	find . -name '__pycache__' -type d -exec rm -rf {} +
