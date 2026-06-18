# File Research: sources/local-fs/squashfs-tools/squashfs-tools/pseudo.c

Full parser and tree manager for pseudo file definitions. It maintains global `pseudo`, a sorted-ish hierarchical tree of `pseudo_entry` nodes, each optionally holding a pseudo device/file definition, child pseudo tree, and pseudo xattrs.

Supported definitions include directories, modifications, block/char devices, dynamic command-backed files, symlinks, sockets/FIFOs, xattrs, hard links to real files, hard links to pseudo files, timestamped extended forms, and `R` data records for unsquashfs-generated pseudo files. It validates modes, uid/gid names or numeric ranges, device major/minor limits, symlink length, and trailing junk.

Dynamic pseudo files run `/bin/sh -c <command>` with stdout piped back. Real hard links can optionally follow symlinks and reject directories and the destination output file. Pseudo-file hard links resolve against already parsed pseudo definitions and reject directory/modify targets.

`read_pseudo_file()` supports stdin or file input, comments, blank lines, backslash line continuations, and the `# START OF DATA - DO NOT MODIFY` marker for embedded data payloads. `R` records force single-threaded reading because data comes from one shared pseudo data file.

Trace builds can dump the pseudo tree; non-trace builds provide a no-op `dump_pseudos()`.
