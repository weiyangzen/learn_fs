# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMat.hh

## Purpose
`XrdSsiShMat.hh` declares the abstract shared-memory table interface. It defines the raw, untyped contract implemented by `XrdSsiShMam` and wrapped by `XrdSsi::ShMap<T>`.

## Important APIs and Types
The interface includes pure virtual methods for `AddItem`, `Attach`, `Create`, `Export`, `DelItem`, `Detach`, two `Enumerate` forms, `Info`, `GetItem`, `Resize`, and three `Sync` forms. `CRZParms` describes create/resize sizing and options. `NewParms` describes implementation name, backing path, type name, type size, and hash ID. Static `New` is the backend factory.

## Control Flow
Callers allocate through `New`, then attach or create, operate through raw buffers keyed by strings and hashes, and eventually detach/delete. Implementations must ensure compatibility checks for type/implementation/hash at attach time.

## State and Persistence
The base stores duplicated strings for implementation, path, type, plus type size and hash ID. The virtual destructor frees those strings but warns derived destructors must detach their own mappings first.

## Dependencies and Integration Points
It has minimal dependencies on C allocation/string headers. `XrdSsiShMam` derives from it; `XrdSsiShMap.hh` provides the typed public API.

## Risks and Test Signals
ABI stability and ownership are central: callers pass raw pointers, and derived classes own external resources. Tests should cover constructor duplication, destructor cleanup, backend attach compatibility, unsupported `Info` names, read-only update failure, and sync behavior delegated through the virtual interface.
