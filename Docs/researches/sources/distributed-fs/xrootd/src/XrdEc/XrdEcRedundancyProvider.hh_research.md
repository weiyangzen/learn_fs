## sources/distributed-fs/xrootd/src/XrdEc/XrdEcRedundancyProvider.hh

### Purpose
This header declares the `RedundancyProvider` class, which computes missing data/parity blocks for a configured erasure-code layout.

### Important APIs, Types, and Functions
- Public `compute(stripes_t &stripes)` reconstructs missing stripe buffers or throws on invalid/unrecoverable input.
- Constructor fixes layout parameters from `ObjCfg`.
- Private `CodingTable` stores ISA-L table bytes, selected healthy block indices, and error count.
- Private `getErrorPattern`, `getCodingTable`, and `replication` support the implementation.

### Control Flow
Consumers construct or retrieve a provider for one layout and repeatedly call `compute` with a full stripe vector. The provider hides decode-table construction and caching behind the public method.

### State and Persistence
State includes an `ObjCfg` copy, encode matrix, decode-table cache keyed by error pattern, and mutex. There is no external persistence.

### Dependencies and Integration Points
The header depends on `XrdEcObjCfg.hh` and `XrdEcUtilities.hh` for layout and stripe descriptors. `XrdEcConfig` caches instances, `Reader` uses them for recovery, and write-buffer code uses them for parity generation.

### Risks and Edge Cases
The contract says blocks can be arbitrary size but equal within a stripe; the implementation uses `objcfg.chunksize`, so caller buffers must be sized accordingly. The class is thread-safe around cache construction but not around caller-owned stripe buffers. Exceptions are the error channel, not status returns.

### Test Signals
Compile tests should catch ISA-L type compatibility. Runtime tests should assert `compute` behavior for valid and invalid stripe vectors, exception propagation, and concurrent calls with identical and distinct error patterns.
