package := gengpt
run     := poetry run
python  := $(run) python
textual := $(run) textual
lint    := $(run) pylint
mypy    := $(run) mypy
black   := $(run) black
isort   := $(run) isort

# Run the application.
.PHONY: run
run:
	$(python) -m $(package)

.PHONY: debug
debug:
	TEXTUAL=devtools make run

# Setup/update packages the system requires.
.PHONY: setup
setup:
	poetry install
	$(run) pre-commit install

.PHONY: update
update:
	poetry update

# Package building and distribution.
.PHONY: build
build:
	poetry build

.PHONY: clean
clean:
	rm -rf dist

# Reformatting tools.
.PHONY: black
black:				# Run black over the code
	$(black) $(package)

.PHONY: isort
isort:				# Run isort over the code
	$(isort) --profile black $(package)

.PHONY: reformat
reformat: isort black		# Run all the formatting tools over the code

.PHONY: lint
lint:
	$(lint) $(package)

.PHONY: typecheck
typecheck:
	$(mypy) --scripts-are-modules $(package)

.PHONY: stricttypecheck
stricttypecheck:
	$(mypy) --scripts-are-modules --strict $(package)

.PHONY: checkall
checkall: lint stricttypecheck # Check all the things

# Utility.
.PHONY: repl
repl:				# Start a Python REPL
	$(python)

.PHONY: shell
shell:
	poetry shell

.PHONY: help
help:				# Display this help
	@grep -Eh "^[a-z]+:.+# " $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.+# "}; {printf "%-20s %s\n", $$1, $$2}'

.PHONY: housekeeping
housekeeping:			# Perform some git housekeeping
	git fsck
	git gc --aggressive
	git remote update --prune