## sources/sync-backup/bup/lib/bup/vint.py

Purpose: implements Bup’s binary variable-length integer and byte-vector encodings, with C helper fast paths and Python fallbacks.

Important APIs and control flow: `encode_vuint()`/`read_vuint()` encode unsigned integers seven bits at a time. `encode_vint()`/`read_vint()` reserve sign information in the first byte. `write_bvec()`, `read_bvec()`, `encode_bvec()`, and `skip_bvec()` handle length-prefixed byte strings. `send()`, `recv()`, `pack()`, and `unpack()` provide simple format strings: `V`, `v`, and `s`.

State and dependencies: stateless; depends on `BytesIO` and `_helpers` C implementations. Fallback code handles overflows from C helpers and raises `ValueError` for negative unsigned values.

Risks and tests: EOF handling is strict for reads, but `skip_bvec()` reads once and only verifies some bytes were returned, so short skips can leave unread bytes if used with nonblocking/partial streams. Format strings reject unknown types. Direct tests are likely in metadata/vint unit tests outside this subset; metadata, repo protocol, and index formats indirectly depend on it.
