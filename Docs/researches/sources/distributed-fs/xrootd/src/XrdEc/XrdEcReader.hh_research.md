## sources/distributed-fs/xrootd/src/XrdEc/XrdEcReader.hh

### Purpose
This header declares the public and private interface for the XrdEc reader that reconstructs logical object reads from erasure-coded zip archives.

### Important APIs, Types, and Functions
- `buffer_t` is `std::vector<char>` for stripe and metadata buffers.
- `callback_t` is a status plus byte-count callback for internal stripe reads.
- `Reader` exposes `Open`, `Read`, `VectorRead`, `Close`, and `GetSize`.
- Private helpers include stripe-level `Read`, metadata and size reads, metadata parsing, missing set handling, vector fallback recovery, and callback generation.
- Friend declarations for `MicroTest`, `XrdEcTests`, and `block_t` expose internals to tests and implementation.

### Control Flow
The public lifecycle is open, read/vector-read zero or more times, then close. Private maps are populated during open and consumed during read mapping. Vector-read recovery coordination uses a mutex, vector of missing chunk ids, and condition variable.

### State and Persistence
The reader holds a reference to `ObjCfg`, archive and metadata maps, zip-entry-to-url mapping, missing stripe set, one cached block, synchronization primitives, last block number, file size, archive indices, and vector-read missing state. It owns no persistent remote objects.

### Dependencies and Integration Points
The header includes XrdEc object config, XrdCl zip archive and operations, and standard containers/synchronization. It is instantiated by `XrdClEcHandler` and implemented in `XrdEcReader.cc`.

### Risks and Edge Cases
`ObjCfg` is held by reference, so the config must outlive the reader. The one-block cache is protected by `blkmtx`, while block internals use their own mutex. `missingChunksVectorRead` tracks tuples globally for the reader, so overlapping vector reads can interfere unless calls are serialized by higher layers.

### Test Signals
Interface tests should validate lifecycle ordering, config lifetime assumptions, concurrent read behavior, size reporting after open, vector-read callback behavior, and close when no archives are open.
