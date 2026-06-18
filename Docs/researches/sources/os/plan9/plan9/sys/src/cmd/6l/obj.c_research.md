# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/obj.c

This is the main amd64 linker driver and object/archive reader. `main` parses linker options, configures output format and segment addresses, initializes opcode coverage and register encoding tables, creates the output file, loads object files, resolves libraries, handles export/import or dynamic module modes, patches/follows code, lays out data and stack offsets, optionally inserts profiling, spans instructions, and emits the final binary.

`objfile` handles regular object files and Plan 9 archives. For archives, it reads `__.SYMDEF`, searches members needed by unresolved `SXREF` symbols, and loads only required objects, repeating until no more references resolve. `loadlib`, `addlibpath`, and `findlib` manage explicit and autolib search paths.

`ldobj` parses `.6` object streams: `ANAME`/`ASIGNAME` symbol records, source history, `TEXT`, `DATA`, `GLOBL`, `DYNT`, `INIT`, `MODE`, `AEND`, branch offsets, duplicate text, float constants converted into data literals, and auto/param metadata. It maintains symbol versions for statics and source history path compression.

The file also implements hunk allocation, instruction allocation/copy/append helpers, profiling insertion, byte-order initialization, IEEE conversions, undefined-import marking, and import/export list reading.

Filesystem relevance is strong: this is the code that reads object and archive files from the filesystem and emits final Plan 9/ELF binaries for OS components.
