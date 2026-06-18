# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/46

Purpose: golden fixture for an ARM-style paging request in block request scatter-gather mapping. Expected title is `BUG: unable to handle kernel paging request in blk_rq_map_sg`, alternate title is `bad-access in blk_rq_map_sg`, type is `MEMORY_SAFETY_BUG`, and `CORRUPTED: Y`.

Important APIs, types, and functions: parser fields cover memory-safety typing and corruption. The key kernel crash frame is `PC is at blk_rq_map_sg+0x70/0x2c0`.

Control flow: the log records a paging request/oops with architecture-specific `PC is at` formatting. The parser must extract the function from PC rather than x86 RIP and set the corrupted bit from expectation metadata.

State and persistence behavior: static corrupted fixture. The file persists a minimal block-layer crash report and does not include panic state.

Dependencies and integration points: depends on architecture-neutral Linux oops parsing, bad-access alternate generation, and corruption expectations in `ParseTest`. Integrates block layer request mapping into report regression coverage.

Risks: short reports provide little fallback context, so missing `PC is at` support would lose the title. Corruption status must not suppress crash detection.

Test signals: paging-request header, `PC is at blk_rq_map_sg+0x70/0x2c0`, expected `MEMORY_SAFETY_BUG`, and `CORRUPTED: Y`.
