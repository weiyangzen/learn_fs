## sources/distributed-fs/xrootd/src/XrdEc/XrdEcRedundancyProvider.cc

### Purpose
This file implements parity generation and missing-stripe recovery using ISA-L erasure-coding primitives, with a replication shortcut when there is one data stripe.

### Important APIs, Types, and Functions
- `gf_gen_decode_matrix(...)` is adapted from ISA-L tests and builds a decode matrix for a known error pattern.
- `RedundancyProvider::RedundancyProvider(const ObjCfg&)` creates a Cauchy encode matrix.
- `getErrorPattern(stripes_t&)` encodes missing/invalid stripes as a binary string.
- `getCodingTable(pattern)` expands the error pattern, builds/caches block indices and ISA-L decode tables.
- `replication(stripes_t&)` fills missing stripes from any healthy stripe for one-data-stripe layouts.
- `compute(stripes_t&)` performs no-op, replication, or erasure-code reconstruction depending on layout.

### Control Flow
`compute` first derives the error pattern. With no parity it returns. With one data stripe it calls replication. Otherwise it obtains a cached coding table for the exact missing pattern, builds input buffer pointers from selected healthy stripes, allocates temporary output buffers for each error, calls `ec_encode_data`, and copies reconstructed buffers back into the missing stripe slots.

`getCodingTable` locks the provider, counts errors and data-source errors, rejects patterns with more errors than parity, computes a decode matrix from the encode matrix and error arrays, initializes ISA-L tables, caches the table, and returns it.

### State and Persistence
Provider state is in an owned `ObjCfg` copy, Cauchy encode matrix, cached coding tables, and mutex. The cache persists for the provider lifetime and is shared by all readers/writers using the same singleton config key.

### Dependencies and Integration Points
This file depends on ISA-L `gf_gen_cauchy1_matrix`, `gf_invert_matrix`, `gf_mul`, `ec_init_tables`, and `ec_encode_data`; it also uses XrdEc utility `stripes_t` and `IOError`. Reader recovery and write-buffer encoding call through `Config::GetRedundancy`.

### Risks and Edge Cases
Variable-length arrays such as `unsigned char* inbuf[objcfg.nbdata]` and `outbuf[dd.nErrors]` rely on compiler extensions in C++. `dd.table.resize(objcfg.nbdata * objcfg.nbparity * 32)` may be larger than needed but should be sufficient for ISA-L table entries. `replication` chooses the last valid stripe encountered. `compute` does not mark `stripes[i].valid` true after recovery; callers must treat filled buffers as valid or update state separately. Error handling throws `IOError`, so callers must catch it.

### Test Signals
Tests should cover no-parity no-op, one-data replication, all single-stripe failures, mixed data/parity failures, too many failures, cache reuse for repeated patterns, checksum-before-recovery expectations, and byte-for-byte reconstruction against known ISA-L examples.
