# sources/distributed-fs/tahoe-lafs/src/allmydata/cli/__init__.py

## Purpose

This is an empty package marker for `allmydata.cli`.

## Important APIs, Types, And Functions

The file defines no symbols.

## Control Flow

Importing `allmydata.cli` executes no package-specific code.

## State And Persistence

There is no state or persistence.

## Dependencies And Integration Points

Its presence makes the CLI package importable and allows sibling modules such as `grid_manager.py` to live under `allmydata.cli`.

## Risks

No direct behavioral risk. Adding import-time behavior here would affect every CLI submodule import.

## Test Signals

`import allmydata.cli` should succeed without side effects.
