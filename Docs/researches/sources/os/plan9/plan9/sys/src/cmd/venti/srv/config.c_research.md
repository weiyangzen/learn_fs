# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/config.c

Parses and initializes Venti server configuration. `runconfig()` reads an `IFile`, accepts directives for `isect`, `arenas`, `bloom`, `index`, memory sizes, `queuewrites`, HTTP address, webroot, and Venti address, and rejects duplicate or malformed lines.

`initventi()` initializes stats, runs the config parser, creates `mainindex` with `initindex()`, and attaches the configured Bloom filter. `configisect()`, `configarenas()`, and `configbloom()` open underlying `Part` objects in direct read/write mode and initialize their on-disk structures.

The parser is deliberately strict: unknown lines, bad sizes, duplicate settings, and illegal names abort initialization. `needmainindex()` exists only to force data-symbol linkage on platforms that need a function reference.
