# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt9660.c

ISO9660 import support for `flfmt`.

It validates a CD image, checks that the fossil data partition overlays the ISO data region correctly, marks ISO-backed fossil data blocks allocated with a fixed tag, and then copies the ISO directory tree into `/active`. Directories are created normally; file contents are mapped by assigning fossil block pointers directly to the existing ISO sectors rather than copying data.

The parser handles ISO9660 volume descriptors, directory records, Plan 9 system-use directory metadata, timestamps, names, and endian-formatted fields. After import it takes an initial snapshot so the installed tree is present in fossil history.
