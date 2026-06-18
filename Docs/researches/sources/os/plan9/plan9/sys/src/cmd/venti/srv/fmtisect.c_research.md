# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtisect.c

Implements `fmtisect`, which formats a single index section. It accepts a section name and target file, with options for block size, version 1 section format, and zeroing.

The command opens the part, optionally zeros it, creates a new `ISect` via `newisect()`, prints bucket count, bucket capacity, and index-map table size, then writes the section header with `wbisect()`.

Defaults are 8 KiB bucket blocks, 512 KiB config table size, and ISect version 2, which includes a randomized bucket magic.
