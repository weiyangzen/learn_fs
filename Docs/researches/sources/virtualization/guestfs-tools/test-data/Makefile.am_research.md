# File Research: sources/virtualization/guestfs-tools/test-data/Makefile.am

Automake directory file for guestfs-tools test data.

Key behavior:
- Includes shared `subdir-rules.mk`.
- Defines subdirectories: `binaries`, `phony-guests`, then `.`.

Research notes:
- This file delegates substantive test-data generation to child directories.
