# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/config.c

Parses Venti server configuration and initializes the global `mainindex`.

Key behavior:
- `initventi` initializes stats, runs config parsing, creates the `Index` from configured sections, and attaches optional Bloom.
- `runconfig` accepts lines for `isect`, `arenas`, `bloom`, `index`, `bcmem`, `mem`, `icmem`, `queuewrites`, `httpaddr`, `webroot`, and `addr`.
- Rejects duplicate singleton settings and illegal names/sizes.
- Dynamically grows arrays of arena partitions and index sections.
- `configisect`, `configarenas`, and `configbloom` open configured files with `initpart` and initialize corresponding objects.

Interactions:
- Uses `IFile` parsing from `ifile.c`.
- Uses `initisect`, `initarenapart`, `readbloom`, and `initindex`.
- Exports global `Index *mainindex`.

Notable details:
- `numok` effectively accepts parsed numbers with optional K/M/G suffixes but currently returns 0 even for trailing non-suffix data due to final `return 0`; caller still uses `unittoull`.
