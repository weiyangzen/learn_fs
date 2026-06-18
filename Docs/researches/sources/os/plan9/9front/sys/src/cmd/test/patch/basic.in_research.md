# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/basic.in

This is a numeric line fixture for patch tests.

Contents:
- 93 lines.
- Starts at `3` and mostly increments through `98`.
- Contains deliberate irregularities: repeated `13`, `12`, missing ranges, and jumps around `39` to `42` and `86` to `88`.

Purpose:
- Serves as an input baseline for a basic patch application test where line identity is simple and visually verifiable.

Risk notes:
- No code or parser logic; correctness is exact fixture content.
