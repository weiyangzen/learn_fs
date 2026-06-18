# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/ifile.c

Provides simple input-file handling for Venti config-like text. `readifile()` opens either a regular config file or a Venti partition-embedded config stored near `PartBlank`, checks the `"venti config\n"` magic for embedded configs, and stores the contents in a `ZBlock`.

`partifile()` reads a text table from a `Part` range, used for replicated index config. `ifileline()` returns the next nonblank line, strips comments beginning with `#`, and removes leading whitespace. `ifilename()` and `ifileu32int()` parse specific line types.

The file is shared by server config parsing and on-disk index configuration parsing.
