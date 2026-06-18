# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/check.c

Filesystem consistency checker for gefs.

Key responsibilities:
- Verifies B-tree ordering, key ranges, balance, pointer validity, and child fill counts through `checktree()`.
- Walks arena free AVL ranges for ordering/overlap errors and verifies allocation-log chains.
- Checks snapshot deadlist records and their linked log blocks.
- Opens every snapshot label and checks its root tree.
- Reports errors to a supplied fd and returns overall ok/broken status.

Important behavior:
- `checkfs()` waits for epochs, then holds `fs->mutlk` while checking global metadata.
- `isfree()` detects block pointers that point into currently free arena ranges.
- Pivot buffer messages are validated for known operation codes and valid `Owstat` masks.

Notable risks:
- `checkdata()` currently scans `Klabel` keys in a data tree while interpreting values as block pointers; this means ordinary `Kdat` file data pointers are not actually covered there.
- Error recovery in the snapshot loop uses nested `waserror()` blocks and continues past some failures.
