# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/__init__.py

## Purpose
Marks `allmydata.test.cli` as a test package. The file is intentionally empty and provides no runtime behavior.

## Important APIs, Types, And Functions
There are no functions, classes, constants, or side effects.

## Control Flow
No control flow exists in this file.

## State And Persistence
No state is held and no persistence occurs.

## Dependencies And Integration Points
The only integration point is Python package discovery/import resolution for CLI tests in the same directory.

## Risks And Test Signals
The main risk is accidental addition of import-time behavior that would affect every CLI test. The expected test signal is simply that relative imports from `allmydata.test.cli` modules resolve.
