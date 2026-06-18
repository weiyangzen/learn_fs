# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/dat.h

Defines core data structures for `hgfs`.

Key points:
- Sets constants:
  - `MAXPATH = 1024`
  - `BUFSZ = 1024`
  - `HASHSZ = 20`
- Declares structures:
  - `Revmap`: one revlog index entry, including revision numbers, parent/base/link revisions, hash, flags, data offsets/lengths, full length, and aux pointer.
  - `Revlog`: opened revlog state, index/data file descriptors, parsed map, temp extraction cache, and refcount.
  - `Revnode`: manifest tree node with name, file hash, qid-derived path, parent/sibling/child links, historical `before` link, and mode.
  - `Revinfo`: parsed changelog metadata, including changelog hash, manifest hash, author, message, time, log offset/length.
  - `Revtree`: refcounted tree wrapper.
  - `Revfile`: per-9P-fid state for current level, revision info/tree/node/revlog, opened temp file, metadata offset, and buffered string.
- Defines global `nullid`.

Dependencies and interactions:
- Included by all `hgfs` C files.
- Structures are populated by `revlog.c`, `info.c`, and `tree.c`, and served by `fs.c`.

Research relevance:
- Central schema for the Mercurial revlog-backed 9P filesystem.
