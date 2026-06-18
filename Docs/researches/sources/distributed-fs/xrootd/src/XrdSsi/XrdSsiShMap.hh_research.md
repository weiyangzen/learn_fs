# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMap.hh

## Purpose
`XrdSsiShMap.hh` defines the public templated typed key/value map API over `XrdSsiShMat`. It lets callers create or attach a shared-memory map for values of type `T` without directly handling raw buffers, implementation selection, or hash identifiers.

## Important APIs and Types
Namespace types include `ShMap_Access`, `ShMap_Parms`, `SyncOpt`, and `ShMap_Hash_t`. `ShMap<T>` exposes `Attach`, `Create`, `Detach`, `Export`, `Add`, `Del`, `Enumerate`, `Exists`, `Get`, `Info`, `Rep`, `Resize`, and `Sync`. The template stores an `XrdSsiShMat*`, optional hash function, type name, and implementation name. The method bodies are included from `XrdSsiShMap.icc`.

## Control Flow
`Create`/`Attach` build `XrdSsiShMat::NewParms`, allocate an implementation through `XrdSsiShMat::New`, and then delegate. Operations compute an optional caller-provided hash before forwarding to the abstract backend. `Attach` retries a bounded number of times on `EAGAIN`, which indicates the backing inode changed while attaching.

## State and Persistence
The template owns only the backend object and duplicated type/implementation strings. Persistence is entirely backend-controlled through the mapped file and explicit `Export`/`Sync`.

## Dependencies and Integration Points
It depends on `XrdSsiShMat` and the inline implementation file. The default implementation is `XrdSsiShMam`, but the abstraction leaves room for alternative `XrdSsiShMat` implementations.

## Risks and Test Signals
Risks include option-bit parsing using high-bit masks, custom hash functions that return zero or unstable hash IDs, type names longer than backend limits, and `Resize(nullptr)` path using default resize parameters. Tests should cover typed create/attach mismatch, custom hash ID compatibility, add/get/replace/delete, enumeration termination, sync options, retry on attach `EAGAIN`, and destructor detach.
