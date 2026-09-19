# Offline scientific tests build their own temporary release under build/.
PYTHON_BIN ?= python3
.PHONY: test
test:
	$(PYTHON_BIN) -B -m unittest discover -s tests -v
