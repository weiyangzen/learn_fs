# File Research: sources/teaching/xv6-public/wc.c

User-space word count utility.

Behavior:
- Counts lines, words, and bytes for stdin or each named file.
- Uses whitespace characters `" \r\t\n\v"` to split words.
- Reads in 512-byte chunks.
- Prints counts plus name and exits on read/open errors.
