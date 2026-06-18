# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/wdir.c

Wiki-directory-relative file access wrappers.

Key behavior:
- Global `wikidir` names the backing wiki directory.
- `wname()` constructs `wikidir/file`.
- `wopen()`, `wcreate()`, `wBopen()`, `waccess()`, and `wdirstat()` wrap Plan 9 file operations after prefixing paths with `wikidir`.

Notable dependencies:
- Allocation helpers from `wiki.h` and Plan 9 file/Bio APIs.

Research notes:
- Each wrapper frees the temporary prefixed pathname after the underlying operation.
