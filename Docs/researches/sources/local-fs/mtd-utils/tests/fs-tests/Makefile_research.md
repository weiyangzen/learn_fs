# File Research: sources/local-fs/mtd-utils/tests/fs-tests/Makefile

## Purpose
Recursive make dispatcher for filesystem test suites.

## Key Elements
Defines `SUBDIRS = lib simple stress integrity utils` and forwards `all`, `clean`, and `tests` targets into each subdirectory.

## Dependencies
Requires each child test directory to provide compatible make targets.

## Behavior/Risks
Simple recursive make wrapper with no explicit ordering constraints besides the listed subdirectory order.
