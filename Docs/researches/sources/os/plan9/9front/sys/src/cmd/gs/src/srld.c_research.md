# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/srld.c

Implements the `RunLengthDecode` stream filter.

Key points:
- Initializes decode state from inline defaults in `srlx.h`.
- Processes literal runs for control bytes less than 128, repeat runs for control bytes greater than 128, and optional EOD at byte 128.
- Maintains suspended copy/repeat state when output space is exhausted or literal input is incomplete.
- `copy_data == -1` marks literal copying; non-negative `copy_data` marks repeated byte output.
- Template minimum input/output sizes are both 1.

Dependencies and interactions:
- Uses `srlx.h` shared run-length state definitions.

Research relevance:
- RunLength decompressor used for PostScript/PDF stream data.
