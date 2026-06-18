# File Research: sources/virtualization/guestfs-tools/test-data/binaries/Makefile.am

Automake file for prebuilt binary fixtures used in phony guest images.

Key behavior:
- Includes shared `subdir-rules.mk`.
- Distributes `README`, `bin-win32.exe`, and `bin-x86_64-dynamic`.

Research notes:
- These fixtures are uploaded into generated Linux/Windows guest images to satisfy inspection or tool heuristics.
