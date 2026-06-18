# sources/distributed-fs/tahoe-lafs/misc/coding_tools/coverage2el.py

## Purpose

This helper converts `.coverage` data into an Emacs Lisp-readable hash table stored in `.coverage.el`, mapping absolute filenames to executable, covered, and uncovered line lists.

## Important APIs, Types, and Functions

`ElispReporter` subclasses `coverage.summary.SummaryReporter` and overrides `report`. It calls `find_code_units`, uses `self.coverage.analysis(cu)`, skips `coverage.misc.NoSource`, and writes Elisp `puthash` forms. `main` loads default coverage data, calls private `_harvest_data`, restricts include paths to `src/*`, and invokes the reporter.

## Control Flow

Execution is linear: instantiate coverage, load data, harvest, set config, write `.coverage.el`. For each code unit, executable lines and missing lines are turned into sorted numeric lists; covered lines are computed as `executable - missing`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is `.coverage.el`. Dependencies are an older coverage.py API and Emacs Lisp consumers. Risks include private `_harvest_data`, unescaped quote/backslash characters in filenames, stale coverage API names, and overwriting `.coverage.el`. Tests should use a tiny coverage database fixture, a missing-source file, and filenames requiring Elisp string escaping.
