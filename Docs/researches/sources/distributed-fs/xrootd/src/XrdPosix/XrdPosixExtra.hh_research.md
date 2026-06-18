## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtra.hh

Purpose: declares the extended POSIX-to-XRootD interface beyond standard POSIX calls.

Important APIs/types: static `XrdPosixExtra::Fctl`, `FSctl`, `pgRead`, `pgWrite`, `PreRead` overloads, and option constant `forceCS`.

Control flow: API comments define sync versus async behavior. For pgread/pgwrite, absence of callback returns byte count or `-1`; callback presence returns `0` and completes later.

State and persistence: class has no fields. Operations act on open file descriptors, cache state, and caller-provided buffers/checksum vectors.

Dependencies/integration: includes `XrdOucCache.hh` for operation codes and range lists, and standard vector/string/POSIX types. Bridges public callers to `XrdPosixFile`/cache internals.

Risks: caller must preserve buffers and checksum vectors until async completion. `void* buffer` for write could be `const void*` semantically but is mutable in signature. `PreRead` documentation promises behavior not yet implemented by source.

Test signals: header/implementation contract for async ownership; range-list preread advertised success; checksum option compatibility with cache plugins.
