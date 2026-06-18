# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/util.c

Common utility support for 9660 tools.

`atom` interns strings in a 1024-bucket hash table so repeated names compare cheaply by pointer in some code paths. `emalloc` zeroes allocations and fails fatally; `erealloc` fails fatally. `struprcpy` uppercases a string copy. `chat` conditionally writes verbose diagnostics when global `chatty` is nonzero.

Integration points: used across directory, conform, descriptor, and main modules.

Risks and notes: interned strings are never freed. `erealloc` does not zero newly allocated tail memory. `atom` depends on process lifetime and is part of conform-map ordering assumptions.
