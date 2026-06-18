# sources/test-tools/lcov/tests/bin/cleantests.py

Purpose: Python cleanup utility for LCOV tests, replacing shell cleanup logic. It removes generated top-level artifacts and recursively runs `make clean` in selected test directories.

Important APIs: CLI accepts positional tests and `-s/--silent`. Functions are `parse_args`, `find_topdir`, `clean_test(base_dir, test_name)`, and `main`.

Control flow and persistence: `find_topdir` prefers current directory with `common.mak`, then `TOPDIR`, then upward search. `main` uses the current directory as the base for requested tests, removes `test.log`, `test.counts`, `test.time`, `test.log.d`, coverage directories, and top-level `*.info`/`*.counts`, then cleans explicit tests or default suite directories. `clean_test` skips `.sh`/`.pl` scripts and runs `make -C <dir> clean -s` for directories with Makefiles, ignoring failures.

Dependencies and integration: called by `common.mak` `clean_subdirs` and top-level Makefiles. Uses Python stdlib `argparse`, `pathlib`, `shutil`, and `subprocess`.

Risks and test signals: broad ignored exceptions can hide cleanup failures. It deletes generated artifacts under discovered topdir, so incorrect `TOPDIR` would be harmful. Tests are practical: run `make clean` after generating fixtures and verify expected artifacts disappear without deleting source tests.
