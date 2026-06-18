# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/rune.c

Small rune-string utility file for the 9660 tools.

`strtorune` converts a UTF string to a NUL-terminated `Rune` array and returns the destination start. `runechr` finds a rune in a NUL-terminated array. `runecmp` lexicographically compares rune arrays.

Integration points: used by Joliet conversion/sorting and UCS-2 writing helpers.

Risks and notes: callers must supply sufficiently large buffers. `strtorune(nil)` returns nil.
