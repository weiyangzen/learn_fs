# File Research: sources/os/plan9/9front/sys/src/cmd/git/get.c

Git fetch/upload-pack client.

Key responsibilities:
- Connects to a remote upload service and reads advertised refs/capabilities.
- Filters refs by branch, heads, tags, and HEAD; validates ref names.
- Resolves local remote-tracking refs to determine already-held objects.
- Negotiates wants and haves, including optional extra local heads.
- Receives sideband or raw pack data, verifies pack SHA-1 trailer, indexes the pack, and renames pack/index files by hash.
- Prints remote/local ref mapping output for callers like clone.

Important behavior:
- `-l` lists refs without fetching.
- Supports `multi_ack`, `side-band`, and `side-band-64k`.
- Sends up to 256 have lines from local refs and queued ancestors.
- Temporary pack files live under `.git/objects/pack/fetch.<pid>.*`.

Notable risks:
- `fail()` formats variadic messages with `snprint` instead of `vsnprint`, so detailed error formatting may be wrong.
- Smart HTTP and multi-round negotiation are intentionally simplified.
