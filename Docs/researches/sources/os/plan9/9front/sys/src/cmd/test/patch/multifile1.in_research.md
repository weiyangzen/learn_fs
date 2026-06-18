# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/multifile1.in

This is the first input file for a multifile patch test.

Contents:
- Same 93-line numeric sequence as `basic.in`.
- Contains repeated and missing values to make patch edits easy to inspect.

Purpose:
- Used with `multifile2.in` to test patches that modify more than one file.

Risk notes:
- Fixture file only; no executable behavior.
