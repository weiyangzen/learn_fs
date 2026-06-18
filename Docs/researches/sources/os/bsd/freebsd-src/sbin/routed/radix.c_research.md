# File Research: sources/os/bsd/freebsd-src/sbin/routed/radix.c

Userland BSD radix tree implementation used for routing table lookup, insertion, deletion, mask handling, and traversal.

Key responsibilities:
- Implements compressed binary radix search over variable-length keys.
- Supports exact lookup, longest-prefix match, masked lookup, and mask-aware search.
- Interns masks in a separate mask radix tree and annotates route subtrees with radix masks.
- Handles normal contiguous masks and non-contiguous masks.
- Inserts routes, duplicate-key entries, and mask chains ordered by specificity/refinement.
- Deletes routes while maintaining duplicate-key chains, parent links, and subtree mask annotations.
- Walks the tree safely even when callback functions delete current nodes.
- Initializes zero/one root keys, mask tree, and radix node-head function pointers.

Dependencies:
- Includes `defs.h`; uses `rtmalloc`, syslog-style logging, and structures declared in `radix.h`.

Notable risks:
- Pointer manipulation is dense and deletion mutates tree topology in place; dangling mask annotations are explicitly treated as serious consistency errors.
- Duplicate-key and non-contiguous-mask ordering rules are subtle and central to correct route selection.
- `max_keylen` must be set before `rn_init()` or initialization cannot allocate proper key buffers.
