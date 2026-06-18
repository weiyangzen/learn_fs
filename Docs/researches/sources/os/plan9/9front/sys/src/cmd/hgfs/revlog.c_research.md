# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/revlog.c

Implements Mercurial revlog opening, index parsing, revision extraction, temp caching, and metadata-header skipping.

Key points:
- `fmktemp()` creates ORCLOSE temp files under `/tmp`.
- `revlogopen()` opens `<path>.i` and optionally `<path>.d`, stores base path, and parses index entries.
- `revlogupdate()` reads 64-byte revlog index entries into `Revmap`, decoding offsets, flags, compressed length, full length, base/link/parent revisions, and node hash.
- Handles inline revlog data by redirecting data offsets into the index file when no `.d` exists.
- `revhash()` returns `nullid` for invalid revisions.
- `hashrev()` linearly maps node hash to revision number.
- Builds revision chains either by previous index entry or bundle parent rule.
- `revlogextract()`:
  - builds the delta chain
  - decompresses the base fulltext or patches via `funzip()`
  - applies patches with `fpatch()`
  - validates reconstructed data using Mercurial SHA-1 parent/content hash
- `revlogopentemp()` caches the last extracted revision per `Revlog` and returns duped fds.
- `fmetaheader()` detects Mercurial `\1\n...\1\n` metadata wrappers and returns the data offset to skip.

Dependencies and interactions:
- Uses `zip.c` for revlog chunk decompression.
- Uses `patch.c` for deltas.
- Used by `fs.c`, `info.c`, and `tree.c`.

Research relevance:
- The low-level Mercurial storage reader that makes the 9P filesystem possible.
