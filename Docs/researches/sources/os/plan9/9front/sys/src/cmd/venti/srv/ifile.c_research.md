# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/ifile.c

Simple text input abstraction for config files and text tables stored either as normal files or embedded in partitions.

Key behavior:
- `readifile` opens a name as a `Part`; if larger than `PartBlank`, treats it as a Venti partition and reads the 8 KiB config area ending at `PartBlank`, requiring magic `venti config\n`.
- For small files, reads the file directly.
- `partifile` reads an arbitrary partition region into an `IFile`.
- `ifileline` returns the next nonblank line, trims leading spaces/tabs/CR, strips `#` comments, and null-terminates the line in-place.
- `ifilename` reads a line into an arena/name-sized field after length validation.
- `ifileu32int` reads a line as a `u32int`.
- `freeifile` frees the backing `ZBlock`.

Interactions:
- Used by config parsing, arena map parsing, and index table parsing.

Notable details:
- For embedded partition configs it adjusts `b->data`, `_size`, and `len` after the magic, with a comment noting `freezblock` constraints.
