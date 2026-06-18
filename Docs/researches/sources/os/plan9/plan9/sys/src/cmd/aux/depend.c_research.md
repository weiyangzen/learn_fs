# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/depend.c

This file implements a 9P filesystem that exposes `.depend` dependency graphs as virtual tar files.

Key behavior:
- Posts a service in `#s/<svc-name>` and serves a filesystem rooted at a supplied directory.
- Real directories are walked normally, but symbols from each directory's `.depend` file appear as `<symbol>.tar` files.
- Parses `.depend` records: `F` source file, `D` defined symbol, and `R` referenced symbol.
- Resolves transitive dependencies into bit vectors of required files.
- Reads of a virtual tar stream synthesize tar headers, source file contents, padding, and trailing zero blocks.

Important details:
- Caches parsed dependency files by path and invalidates them when their qid changes.
- Source filenames may resolve to `.Z` or `.gz` variants if the plain file is absent.
- Directory reads include subdirectories first, then virtual tar dependency files.
- Service is read-only; create, write, remove, and wstat are denied.
- Multiple `fsrun` processes share the mounted pipe with an I/O lock.

Filesystem relevance:
- Direct: synthetic filesystem overlay that materializes dependency closure archives on demand.
