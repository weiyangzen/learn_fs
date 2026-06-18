# sources/security-integrity/selinux/python/sepolgen/tests/Makefile

## Purpose
This Makefile is the local test harness for sepolgen's Python unit tests. It centralizes cleanup of generated parser, bytecode, module-compile, and test-output artifacts, and invokes the aggregated `run-tests.py` runner.

## Important Targets And Variables
`PYTHON ?= python3` controls the interpreter. `test` runs `$(PYTHON) run-tests.py`. `clean` removes backups, bytecode, yacc table/debug files (`parser.out`, `parsetab.py`), module compiler outputs (`module_compile_test.fc`, `.if`, `.pp`), generic `output`, `__pycache__`, and `tmp`.

## Control Flow
The only executable workflow is `make test`, which delegates all discovery/import ordering to `run-tests.py`. `make clean` is manual hygiene around tests with file-system side effects.

## State And Persistence
The Makefile does not persist state itself, but it acknowledges several tests create local files. `test_interfaces.py` writes `output`, parser generation may write `parser.out` and `parsetab.py`, and `test_module.py` creates compiled SELinux module artifacts.

## Dependencies And Integration Points
It depends on the Python unit test suite in the same directory and any external SELinux toolchain needed by those tests. It is tightly coupled to exact generated filenames; if module compiler output names change, cleanup will become stale.

## Risks And Edge Cases
The cleanup target uses broad globs such as `*~` and `*.pyc` but is scoped to the test directory. The test target does not set environment variables, so it relies on `run-tests.py` to adjust `sys.path` and on the caller's working directory for fixtures like `audit.txt`, `perm_map`, and `module_compile_test.te`.

## Test Signals
The presence of cleanup for parser and module artifacts signals expected side effects from parser generation and external SELinux module compilation. Successful `make test` should leave only ignored or cleanup-removable outputs.
