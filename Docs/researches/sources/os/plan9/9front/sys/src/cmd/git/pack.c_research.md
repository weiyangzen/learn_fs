# File Research: sources/os/plan9/9front/sys/src/cmd/git/pack.c

Core git object and packfile implementation. It manages object lifetime, parsing, caching, loose object reads, packed object reads, delta application, pack index lookup, prefix expansion, pack indexing, reachability scanning, delta selection, and pack writing.

Read path: `readobject` loads from cache, pack indexes, or loose objects. Packed objects support commit/tree/blob/tag plus offset and ref deltas; deltas are decompressed and applied to base objects. Loose objects are zlib-inflated and parsed. Commit parsing extracts tree, parents, author, committer, timestamps, and message, dropping signature blocks. Tree parsing validates names and maps git modes to Plan 9 directory metadata, symlink, and submodule markers.

Pack index path: `searchindex` reads v2 `.idx` fanout tables and handles 32-bit and 64-bit offsets. `indexpack` validates PACK v2 input, iteratively resolves deltas until all objects are valid, computes object CRCs, sorts by hash, and writes a v2 index with fanout, hashes, CRCs, offsets, pack hash, and index hash.

Write path: `writepack` computes objects reachable from `ours` but not `theirs`, loads commits/trees/blobs into metadata, chooses deltas in a small sliding window, and emits PACK v2 data with zlib-compressed whole objects or ref/offset deltas. This file is the storage substrate used by fetch, push, serve, and repack.
