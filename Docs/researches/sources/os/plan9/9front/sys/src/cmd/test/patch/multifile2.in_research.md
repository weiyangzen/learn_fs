# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/multifile2.in

This is the second input file for a multifile patch test.

Contents:
- 21 lines.
- Decimal values from `77777` through `77797`.

Purpose:
- Distinct large-number sequence makes it easy to verify that a multifile patch touched the intended second file.

Risk notes:
- Fixture file only; exact line ordering is the contract.
