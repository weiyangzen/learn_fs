# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCache.cc

## Purpose
Implements default synchronous helper methods for the cache I/O abstraction.

## Important APIs and control flow
`XrdOucCacheIO::pgRead()` performs a plain `Read()` into the caller buffer, then, when bytes were read and `forceCS` is set, computes page checksums with `XrdOucPgrwUtils::csCalc()` using the file offset and byte count. `pgWrite()` ignores checksum inputs by default and forwards to plain `Write()`.

`ReadV()` iterates each `XrdOucIOVec` segment, calls scalar `Read()`, and requires every segment to return exactly the requested size; a short positive read is converted to `-ESPIPE`, and errors are returned immediately. `WriteV()` mirrors that behavior for scalar `Write()`.

## State, dependencies, and integration
The implementation is stateless. It depends on `XrdOucCache.hh`, `XrdOucPgrwUtils.hh`, `XrdSys::PageSize` indirectly through checksum utilities, and errno constants. Concrete cache/source implementations inherit these defaults unless they provide optimized page or vector I/O.

## Risks and test signals
The default vector methods do not support partial completion semantics; callers get `-ESPIPE` for short reads/writes after earlier segments may have succeeded. `pgWrite()` does not verify or store caller-provided checksums. Tests should exercise force-checksum reads, vector short-read/short-write behavior, negative error propagation, and concrete overrides that need different semantics.
