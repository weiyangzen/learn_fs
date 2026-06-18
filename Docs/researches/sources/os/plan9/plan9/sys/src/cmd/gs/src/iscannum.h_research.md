# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscannum.h

Purpose: declares `scan_number`, the numeric-token parser used by the main scanner.

Contract: the function scans a byte range with a supplied sign into a `ref`, returns 0 for full consumption, returns 1 for a valid numeric prefix plus trailing data, and leaves `l_new` marking to the caller. The final boolean parameter enables PDF invalid-number compatibility behavior.
