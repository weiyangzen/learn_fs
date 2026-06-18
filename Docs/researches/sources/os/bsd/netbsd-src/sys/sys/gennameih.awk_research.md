# File Research: sources/os/bsd/netbsd-src/sys/sys/gennameih.awk

Read completely: 96 lines.

## Purpose
Generates `namei.h` and `rump_namei.h` from `namei.src`, adding prefixed variants of `NAMEIFL` flags.

## Main Interfaces
- `getrcsid(idstr)`: extracts RCS id content.
- `printheader(outfile)`: writes generated-file warning and provenance.
- `BEGIN`: sets script version, output files `namei.h` and `../rump/include/rump/rump_namei.h`.
- First input line becomes source file header.
- `NAMEIFL` lines are converted into `#define` lines and remembered as `NAMEI_` flags.
- `END`: appends `NAMEI_` defines to `namei.h` and `RUMP_` defines to rump header.

## Dependencies And Integration
Used by the build process in `src/sys/sys` for namei flag header generation.

## Risks And Edge Cases
- Output paths are relative to the working directory where awk is run.
- Field parsing with `-F` relies on the source line structure.
- Generated headers must remain synchronized with `namei.src`.

## Filesystem Relevance
High. `namei` is central pathname lookup infrastructure for VFS.
