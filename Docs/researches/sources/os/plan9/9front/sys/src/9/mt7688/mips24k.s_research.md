# File Research: sources/os/plan9/9front/sys/src/9/mt7688/mips24k.s

This assembly include defines MIPS 24K/MIPS32r2 instruction and macro helpers. It supplies register aliases, `NOOP`, `RETURN`, constant construction, `GETMACH`, polled UART `PUTC`, interrupt enable/disable encodings, `EHB`, `SYNC`, `WAIT`, hazard-barrier return macros, LL/SC, CP0 selected register access, RDHWR, and cache operation encodings.

It is included by `l.s` and keeps CPU-specific instruction encodings out of the main assembly body. The macros are important for exception return, cache maintenance, atomic operations, and hazard-safe CP0 updates.

Filesystem relevance is indirect but critical through atomic locking, cache/TLB correctness, and user/kernel exception return stability.

Notable risks: raw `WORD` encodings are architecture-specific and assembler-sensitive; cache op macros rely on Plan 9 assembler syntax tricks.
