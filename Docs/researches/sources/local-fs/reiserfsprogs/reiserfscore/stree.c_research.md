# File Research: sources/local-fs/reiserfsprogs/reiserfscore/stree.c

Internal tree search helper implementation for ReiserFS userspace code. This file provides key comparison, binary search, path release, delimiting-key lookup, and root-to-leaf traversal.

Major responsibilities:
- Determines whether a buffer is in the tree with `B_IS_IN_TREE()`.
- Compares ReiserFS keys via `comp_short_keys()`, `comp_keys_3()`, and `comp_keys()`.
- Implements generic node-array binary search in `bin_search()`.
- Defines sentinel `MIN_KEY` and `MAX_KEY`.
- Computes left/right delimiting keys with `get_lkey()` and `get_rkey()`.
- Verifies whether a searched key belongs under a path buffer using `key_in_buffer()`.
- Releases all buffers in a search path with `pathrelse()`.
- Descends the formatted tree from root in `search_by_key()` until the requested stop level.

Important implementation details:
- Key comparison reads little-endian fields through `d32_get()` and compares short key, offset, then type.
- `bin_search()` returns both found/not-found status and the insertion/search position.
- Delimiting-key lookup walks parent path elements upward and validates parent child pointers against the child buffer block number.
- `search_by_key()` releases any existing path first, reads blocks with `bread()`, validates tree membership and expected level, then chooses the next child pointer based on binary-search result.

Dependencies and interactions:
- Uses core ReiserFS structures/macros from `includes.h`: block headers, internal keys, child pointers, item heads, path elements, root block, and tree height.
- Complements higher-level search wrappers in `reiserfslib.c`; both provide similar tree traversal services for different call sites.

Risks and notes:
- Structural anomalies panic rather than returning recoverable errors in several places.
- `key_in_buffer()` depends on path consistency; stale or corrupt parent paths become fatal.
- The file comment lists additional mutation helpers that are not present in this excerpt, so this file appears to be a trimmed or refactored subset of older `stree.c` functionality.
