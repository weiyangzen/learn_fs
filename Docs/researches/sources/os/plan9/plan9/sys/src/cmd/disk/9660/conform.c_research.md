# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/conform.c

Manages conforming ISO 9660 names and `_conform.map` output.

A global `Conform *map` stores `Tx` mappings from original atomized names to generated conforming names. `txsearch` binary-searches this array by atom pointer. `addtx` inserts a new mapping, preserving sorted order and warning on duplicates. `conform` returns an existing mapping or creates `Dnnnnnn`/`Fnnnnnn` names for directories/files.

`wrconform` writes new mappings as text lines `good bad` at the current image end, sorted by generated good name for output, then restores map order by original-name atom. It reports the block and byte length to the caller and pads to a block boundary.

Integration points: `direc.c` calls `conform` during name conversion; `dump.c` reconstructs mappings with `addtx`; `dump9660.c` writes full or incremental `_conform.map`.

Risks and notes: sorting by atom pointer, not string, depends on the process-wide string interning table. The generated names are sequential based on map size and can change if map reconstruction changes.
