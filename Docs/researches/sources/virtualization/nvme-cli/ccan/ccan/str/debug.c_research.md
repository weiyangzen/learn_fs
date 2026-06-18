# File Research: sources/virtualization/nvme-cli/ccan/ccan/str/debug.c

- Purpose: debug wrappers for ctype and string functions.
- Build condition: only active under `CCAN_STR_DEBUG`.
- Key behavior: asserts ctype inputs are in `[-1, 255)` before calling libc ctype functions.
- Const handling: provides out-of-line wrappers for `strstr`, `strchr`, and `strrchr` used by debug macros.
