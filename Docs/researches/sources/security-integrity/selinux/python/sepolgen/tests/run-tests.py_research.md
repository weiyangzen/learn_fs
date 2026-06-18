# sources/security-integrity/selinux/python/sepolgen/tests/run-tests.py

## Purpose
This is the aggregate unittest runner for sepolgen. It makes the local source tree importable and imports every test module so `unittest.main()` can discover their `TestCase` classes.

## Important APIs And Flow
The runner inserts `../src/.` at the front of `sys.path`, then imports all tests with wildcard imports: access, audit, refpolicy, refparser, policygen, matching, interfaces, objectmodel, and module. When invoked as a script it calls `unittest.main()`.

## State And Persistence
It mutates process import state by prepending the local sepolgen source directory to `sys.path`. It does not write files directly, but imported tests do.

## Dependencies And Integration Points
It depends on the test files being importable from the current directory and on sepolgen modules being available under `../src/.`. The import order matters only insofar as wildcard imports can overwrite globals; unittest discovery finds classes regardless.

## Risks And Edge Cases
Wildcard imports make namespace collisions possible and obscure which module defines a test name. The script assumes it is run from the tests directory; from another working directory, `../src/.` and local fixture files may not resolve correctly. It uses legacy unittest aggregation rather than explicit discovery.

## Test Signals
It is the authoritative entry point for the tests in this subset and is invoked by the tests Makefile. A passing run exercises parser, policy model, access vector, audit parsing, interface, object model, policy generation, matching, and module compiler behaviors.
