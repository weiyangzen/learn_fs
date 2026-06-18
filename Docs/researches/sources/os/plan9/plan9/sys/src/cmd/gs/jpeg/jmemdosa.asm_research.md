# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemdosa.asm

8086 MASM-compatible assembly support for `jmemdos.c`. It exposes far-callable routines for DOS file I/O, XMS driver calls, and EMS driver calls.

Implemented entry points:

- `_jdos_open`, `_jdos_close`, `_jdos_seek`, `_jdos_read`, `_jdos_write`
- `_jxms_getdriver`, `_jxms_calldriver`
- `_jems_available`, `_jems_calldriver`

The DOS helpers use interrupt `21h` for file create/close/seek/read/write and return zero on success. The XMS helper discovers the driver via interrupt `2Fh` and calls its far entry point with register context loaded from a C struct. The EMS helper checks for `EMMXXXX0` at interrupt vector `67h` and calls interrupt `67h` with a supplied context. All procedures save and restore broad register sets for compiler compatibility.
