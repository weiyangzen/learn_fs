# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/info.c

Parses changelog revision metadata into `Revinfo`.

Key points:
- Extracts a changelog revision into a temp file via `revlogopentemp()`.
- Skips Mercurial metadata header with `fmetaheader()`.
- Reads:
  - manifest hash line into `mhash`
  - author line into `who`
  - timestamp line into `when`
  - changed-file list region, recording `logoff` and `loglen`
  - commit message into `why`
- Stores the changelog node hash into `chash`.
- Cleans up file descriptors and allocated strings on parse failure.

Dependencies and interactions:
- Called by `fs.c` when revision metadata is needed.
- `tree.c` uses `Revinfo` to load manifests and changed-file subsets.

Research relevance:
- Converts raw Mercurial changelog text into structured metadata exposed by the 9P filesystem.
