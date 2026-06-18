# File Research: sources/os/plan9/9front/sys/src/cmd/venti/copy.c

Purpose: Recursively copies a Venti block graph from one Venti server to another.

Key behavior:
- Parses source host, destination host, and a starting score; optionally detects type or uses `-t`.
- Walks root, directory, pointer, and data blocks; root blocks recurse into previous roots and root scores.
- For directory blocks, unpacks active `VtEntry`s and walks their scores by entry type.
- For pointer blocks, walks non-zero child scores with type decremented.
- Writes each block to the destination and verifies score stability unless rewrite mode is enabled.
- Supports fast skipping when the destination already has a block, ignore-errors mode, rewrite-missing mode, visited-score memoization, and verbosity.

Dependencies:
- Uses Venti read/write/root/entry APIs, SHA1, AVL trees, and bin allocation.

Notable details:
- `-r` rewrites unreadable child scores to zero and repacks parents, changing the graph and reporting pointer changes.
