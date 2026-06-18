# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jmemdosa.asm

Purpose: 8086 MASM-compatible assembly support for `jmemdos.c`.

Implemented entry points:
- `_jdos_open`
- `_jdos_close`
- `_jdos_seek`
- `_jdos_read`
- `_jdos_write`
- `_jxms_getdriver`
- `_jxms_calldriver`
- `_jems_available`
- `_jems_calldriver`

Important behavior:
- DOS helpers use interrupt `21h` for file create, close, seek, read, and write.
- Return convention is zero on success for DOS file helpers.
- XMS driver discovery uses interrupt `2Fh`.
- XMS calls load register context from a C structure and call the driver far entry point.
- EMS availability checks for `EMMXXXX0` at interrupt vector `67h`.
- EMS calls use interrupt `67h` with supplied register context.
- Procedures save and restore broad register sets for compiler compatibility.

Notes:
- Exists only for the DOS backing-store backend.
