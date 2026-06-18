# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/Makefile

## Purpose
Delegating makefile for stress tests.

## Key Elements
Defines `SUBDIRS = atoms`, forwards `all`, `tests`, and `clean` to subdirectories, and removes `run_pdf_test_file_*` during clean.

## Dependencies
Requires recursive make.

## Behavior/Risks
No direct binaries here; all work is delegated to `stress/atoms`.
