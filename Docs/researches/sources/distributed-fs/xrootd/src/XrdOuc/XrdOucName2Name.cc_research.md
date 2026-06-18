<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.cc

Purpose: Provides the built-in default implementation of the name translation plugin interface.

APIs and control flow: `XrdOucN2N` implements `lfn2pfn()`, `lfn2rfn()`, `pfn2lfn()`, and `n2nVec()`. The constructor normalizes local and remote roots. `concat_fn()` prefixes a root and inserts a slash when needed. `pfn2lfn()` strips the local root when present. The exported `XrdOucgetName2Name()` creates the mapper and stores it in global `XrdOucN2NVec_P` for optional vector translation.

State and persistence: The object owns duplicated local/remote root strings and returns heap-allocated vectors from `n2nVec()` that must be recycled by the interface contract. No filesystem state is persisted.

Dependencies and integration: Used by `XrdOucN2NLoader` when no external namelib is configured. Integrates with `XrdSysError` for path-length diagnostics.

Risks and test signals: Root stripping requires `pfn[LocalRootLen] == '/'`, so exact-root PFNs are not stripped. Tests should cover null roots, trailing slash normalization, relative LFNs, buffer exhaustion, RFN prefixing, and vector recycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.cc -->
