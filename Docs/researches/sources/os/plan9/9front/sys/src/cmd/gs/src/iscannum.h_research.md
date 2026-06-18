# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscannum.h

Declares `scan_number`, the Ghostscript interpreter number scanner. The interface accepts a byte span, a pre-parsed sign, destination `ref`, output pointer for the first unconsumed byte, and a PDF compatibility flag.

The header notes that `scan_number` does not mark the resulting ref as new; callers such as `iscan.c` apply that marking where appropriate.
