# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil2.h

Purpose: declares Level 2 password helper types and APIs.

Defines `MAX_PASSWORD` as 64, the `password` struct with size plus fixed byte buffer, and `NULL_PASSWORD`. Declares parameter-list password read/write/check routines and dictionary password read/write routines.

The header notes that `MAX_PASSWORD` must match initial password lengths in `gs_lev2.ps`.
