<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mtd.c -->
# sources/test-tools/strace/src/mtd.c

Purpose: decodes Memory Technology Device ioctls and associated ABI structures.
Important APIs/types/functions: `mtd_ioctl`, mpers `struct_mtd_oob_buf`, decoders for erase info, OOB buffers, OTP info, write requests, MTD info, NAND OOB/ECC layouts, ECC stats, and xlat tables for modes/types/flags.
Control flow: switch by ioctl code; writes decode on entry, reads often wait for exit; `MEMGETREGIONINFO` prints a partial struct on entry and completes it on successful exit. Unknown commands fall back to generic decoded state.
State and persistence behavior: stateless tracee-memory reads; relies on syscall phase. Dependencies and integration points: central ioctl dispatcher and mpers generation for old OOB buffer layout.
Risks: many structs are version/word-size sensitive; entry/exit split for read ioctls must match kernel direction. Test signals: fixtures for erase, OOB 32/64, MEMWRITE, OTP, info, ECC, badblock, and region info commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mtd.c -->
