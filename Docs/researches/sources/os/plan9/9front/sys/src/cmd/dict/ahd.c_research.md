# File Research: sources/os/plan9/9front/sys/src/cmd/dict/ahd.c

Purpose: American Heritage Dictionary backend for the Plan 9 `dict` command, handling encrypted entry text.

Key behavior:
- `ahdprintentry()` decrypts bytes with `byte ^ (offset >> 1)`, maps selected high bytes to runes, interprets `%@tag@%` markup, and prints formatted output.
- For command `h`, it stops at tag `EH`.
- For command `r`, it preserves markup tags in output.
- Temporarily sets `breaklen` to 80 while printing.
- `ahdnextoff()` scans encrypted dictionary data for definition delimiters, tracking patterns `%@NL@%` then `%@2@%`.
- `ahdprintkey()` reports that pronunciations are unavailable.

Notable details:
- `intab` initializes special accented and symbol mappings, then fills identity mappings for other byte values on first use.
