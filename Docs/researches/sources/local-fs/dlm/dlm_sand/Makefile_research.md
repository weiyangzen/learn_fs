# File Research: sources/local-fs/dlm/dlm_sand/Makefile

This Makefile builds the `dlm_sand` executable.

Key settings:
- Default install-style variables: `PREFIX=/usr`, `LIBNUM=/lib64`, `BINDIR=$(PREFIX)/sbin`.
- `USE_SD_NOTIFY ?= yes` is defined but not directly used in this file fragment.
- Binary target: `dlm_sand`.
- Sources: `action.c`, `config.c`, `crc32c.c`, `log.c`, `main.c`, and `ondisk.c`.
- Includes: `../include` and `../dlm_controld`.
- Compiler flags emphasize hardening and warnings: `_FORTIFY_SOURCE=2`, stack protector, stack clash protection, PIE, relro/now.
- Libraries: `pthread`, `rt`, `uuid`, and `sanlock`.

Targets:
- `all` builds `dlm_sand`.
- `clean` removes objects, shared libraries, and the binary.
