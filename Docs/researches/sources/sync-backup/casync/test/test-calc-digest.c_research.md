# sources/sync-backup/casync/test/test-calc-digest.c

Purpose: command-line helper that calculates a selected casync digest over files/stdin.

Important APIs/types/functions: parses digest type argument, streams file bytes through `CaDigest`, and prints the resulting hex digest.

Control flow/state: opens each requested file or stdin, reads in blocks, updates digest, finalizes once input is exhausted.

Dependencies/integration: used by NBD/script tests to compare casync CLI digest output against library digest calculation.

Risks/test signals: a bug here can mask or falsely report digest regressions in shell tests, but known-vector `test-cadigest.c` provides an independent check.

Source research group: `subset-b-009122`.
