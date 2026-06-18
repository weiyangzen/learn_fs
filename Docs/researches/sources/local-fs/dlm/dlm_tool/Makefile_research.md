# File Research: sources/local-fs/dlm/dlm_tool/Makefile

## Purpose
Builds and installs the `dlm_tool` administrative CLI and its man page.

## Build Behavior
- Compiles `main.c` into `dlm_tool`.
- Uses hardening flags: PIE, RELRO, immediate binding, stack protector, fortify, stack clash protection.
- Includes headers from `../include`, `../libdlm`, `../dlm_controld`, and `../dlm_sand`.
- Links against `libdlm`, `libdlmcontrol`, and pthreads.
- Installs binary to `$(PREFIX)/sbin` and `dlm_tool.8` to man8.

## Notes
- The Makefile assumes local build products for `libdlm` and `libdlmcontrol` via `-L../libdlm -L../dlm_controld`.
