# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/hash.c

Implements hash formatting, parsing, qid conversion, and Mercurial revision hashing.

Key points:
- `Hfmt()` formats a 20-byte SHA-1 hash as lowercase hex for `%H`.
- `fhash()` computes a Mercurial-style node hash by hashing parent hashes in lexicographic order followed by file contents.
- `hex2hash()` parses up to 40 hex characters into a 20-byte buffer and returns bytes parsed.
- `hash2qid()` maps the first eight hash bytes into a `uvlong` qid path.
- `readhash()` reads a named metadata file under a path, skips an optional `rev.hash` prefix before `.`, and parses the hash.

Dependencies and interactions:
- Uses Plan 9 libsec SHA-1.
- Used by revlog validation, qid generation, revision lookup, and ancestor/update tools.

Research relevance:
- Defines how Mercurial SHA-1 node IDs become filesystem names and qids in `hgfs`.
