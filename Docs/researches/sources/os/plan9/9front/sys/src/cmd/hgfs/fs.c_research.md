# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/fs.c

Implements the main read-only `hgfs` 9P server over a Mercurial repository.

Key points:
- Exposes a namespace rooted at revisions, where each revision directory contains:
  - `rev`, `rev1`, `rev2`
  - `log`, `who`, `why`
  - `files`
  - `changes`
- Opens `.hg/store/00changelog` and `.hg/store/00manifest` as revlogs.
- Lazily opens per-file revlogs under `.hg/store/data`, with fallback to filename mangling for Mercurial store encodings.
- Caches unused file revlogs and evicts idle revlogs when too many are free.
- Caches a small number of loaded revision trees by loader function and `Revinfo`.
- Builds 9P `Qid`s from revision hashes and manifest node hash-derived paths.
- Parses revision names by integer revision, `tip`, full/partial hash, or `rev.hash` style names.
- Walk logic supports:
  - revision directories from root
  - fixed metadata files under a revision
  - manifest trees for all files or changed files
  - file historical revisions through `.revN` suffixes
- Opens changelog/file data by extracting revlog revisions to temp files.
- Skips Mercurial metadata headers in extracted file data via `fmetaheader()`.
- Directory reads are generated through `dirread9p`.
- Serves only read/execute where applicable; write operations are denied.
- `main()` mounts the server at `/mnt/hg` by default or posts a service, with optional 9P debugging.

Dependencies and interactions:
- Uses Plan 9 `<9p.h>`, `<fcall.h>`, `<auth.h>`, `<flate.h>`.
- Relies on `revlog.c`, `tree.c`, `info.c`, `hash.c`, and `util.c`.
- Consumers such as `ancestor.c` and `hgdb.c` read the mounted tree.

Research relevance:
- The core filesystem-facing part of `hgfs`: a read-only versioned 9P view of Mercurial history, manifests, file contents, and changelog metadata.
