# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/tapefs.h

This header defines shared tapefs structures, constants, byte-order helpers, globals, and backend hooks.

Key contents:
- Little-endian and big-endian byte extraction macros.
- `Fid`, `Ram`, `Idmap`, and `Fileinf` structures.
- Permission bit aliases used by tapefs permission checks.
- Global state declarations for root ram tree, user/group maps, repletion, block size, and qid path counter.
- Backend/function prototypes for population, directory expansion, reads, writes, truncation, creation, path insertion, and id mapping.

Important details:
- `Ram` nodes store qid, mode, ownership, times, archive address/data, size, tree links, and lazy population state.
- Backends provide archive-specific `populate`, `popdir`, `doread`, and no-op write/truncate/create behavior.

Filesystem relevance:
- Central: shared ABI between the tapefs 9P server and all archive/filesystem backends.
