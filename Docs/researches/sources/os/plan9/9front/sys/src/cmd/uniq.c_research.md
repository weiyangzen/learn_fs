# File Research: sources/os/plan9/9front/sys/src/cmd/uniq.c

This is a Plan 9 implementation of `uniq`. It reads adjacent lines, compares them after optional field and character skipping, and prints according to mode.

Supported options include `-u` unique-only, `-d` duplicate-only, `-c` counts, `-s` prefix mode behavior in `equal()`, numeric `-N` field skip, and `+N` character skip. It uses fixed `Bsize` line buffers and exits on too-long lines.

The implementation tracks duplicate counts in `linec` and a `uniq` flag set by successful equality comparisons.
