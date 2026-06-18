<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/cacheflush.c -->
## sources/test-tools/strace/src/cacheflush.c

Purpose: Provides architecture-specific decoders for the `cacheflush` syscall variants.

Important APIs and types: Defines `SYS_FUNC(cacheflush)` under mutually exclusive architecture guards: `M68K`, `BFIN || CSKY`, `SH`, and `NIOS2`.

Control flow: Each implementation prints the argument order used by that architecture. M68K prints address, scope, flags, and length. BFIN/CSKY print address, length, and cache flag xlat. SH prints address, length, and flag bitset. NIOS2 prints address and length from argument 3 while ignoring scope/cache-type fields.

State and persistence: No persistent state.

Dependencies and integration: Depends on `defs.h`, optional `<asm/cachectl.h>`, and architecture-specific cacheflush xlat tables.

Risks: Argument positions differ by architecture, so accidental cross-architecture reuse would be wrong. Some fields are intentionally ignored on NIOS2.

Test signals: Architecture-specific syscall tests should verify printed argument names, flag xlat strings, and unsupported-architecture exclusion at build time.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/cacheflush.c -->
