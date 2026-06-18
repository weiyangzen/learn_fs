# sources/test-tools/strace/src/linux/generic/asm_stat.h

Purpose: defines generic Linux `struct stat` compatibility layout metadata for decoders.

Important APIs/types/functions: STRACE_ASM_STAT_H, dev_t, gid_t, ino_t, loff_t, mode_t, nlink_t, off64_t; notable register references include none in this file.

Control flow: no direct flow; stat-family syscall decoders include the layout when printing traced buffers.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on Linux asm/stat ABI definitions and strace stat decoders.

Risks/test signals: wrong field sizes or ordering misprint stat buffers; test stat/lstat/fstat variants.

Source-read signal: reviewed complete local file (57 lines).
