# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/io.c

This file implements exportfs’s main 9P message loop, reply encoding, fid allocation, file cache management, qid uniqueness, and allocation/fatal helpers.

Key responsibilities:
- Reads 9P messages from stdin, decodes them, and dispatches through `fcalls`.
- Encodes and writes replies in `reply`.
- Sends an initial mount error response in `mounterror`.
- Manages fid lookup/allocation/free lists.
- Allocates and recycles `Fsrpc` buffers.
- Maintains cached `File` trees with parent/child links and reference counts.
- Builds local paths from cached file ancestry with `makepath`.
- Maps local qids to unique exported qids with `Qidtab`, collision handling, and high-bit uniqueness.
- Initializes root and pseudo mount-point cache in `initroot`.
- Implements fatal shutdown by killing slave children.

Important implementation notes:
- `uniqueqid` preserves the low 48 bits of local qid path and uses upper bits to resolve collisions.
- `freefile` recursively releases parent refs as child refs drop to zero.
- `freefid` unmounts pseudo mounts associated with fids.
