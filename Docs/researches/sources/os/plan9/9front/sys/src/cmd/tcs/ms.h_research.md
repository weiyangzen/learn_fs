# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/ms.h

This header is a generated-style lookup-table bundle for `tcs`, Plan 9's character set converter. It contains `long tabcpNNN[256]` tables mapping Microsoft/OEM single-byte code page byte values to Unicode rune values.

Key contents:
- A leading commented rc pipeline documents how the tables were originally generated from Microsoft code-page reference pages.
- Tables include IBM/OEM pages such as `cp437`, `cp720`, `cp737`, `cp775`, `cp850`, `cp852`, `cp855`, `cp857`, `cp858`, `cp862`, `cp866`, `cp874`.
- Tables include Windows pages `cp1250` through `cp1258`.
- Valid byte mappings are Unicode scalar values stored as `long`; unmapped bytes are represented as `-1`.

Integration:
- Included by `tcs.c`.
- Entries are registered in `convert[]` under names such as `ibm437`, `windows-1252`, and aliases like `microsoft`.
- Used by table-driven input conversion through `intable()` and output conversion through `outtable()`.

Risk notes:
- This file is pure static data, but table correctness is critical: `-1` entries trigger conversion errors unless `-c` clean mode is enabled.
- Vietnamese `windows-1258` includes combining marks such as `0x0300`, so downstream Unicode normalization/output behavior matters.
