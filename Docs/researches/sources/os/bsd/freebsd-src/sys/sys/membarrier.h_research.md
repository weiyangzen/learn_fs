# File Research: sources/os/bsd/freebsd-src/sys/sys/membarrier.h

Defines FreeBSD membarrier command ABI.

Key content:
- `enum membarrier_cmd` values are bit flags; `MEMBARRIER_CMD_QUERY` returns supported commands as a bitset and itself has value zero.
- Commands include global/shared barrier, global expedited, registration for global expedited, private expedited, private expedited sync-core, registration variants, RSEQ compatibility constants, and current-registration query.
- RSEQ command constants are defined for source compatibility but explicitly not supported by query.
- `enum membarrier_cmd_flag` defines `MEMBARRIER_CMD_FLAG_CPU`.
- Userland prototype: `int membarrier(int, unsigned, int);`

Research relevance:
- Provides userspace-visible memory ordering and synchronization ABI.
- Relevant to runtime libraries and lock-free algorithms rather than filesystem code directly, but can affect kernel/user synchronization assumptions in tests.

Cautions:
- Query support mask is authoritative; defined constants are not necessarily implemented.
- Header is small and ABI-focused, with kernel implementation elsewhere.
