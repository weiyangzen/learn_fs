<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2No2p.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2No2p.cc

Purpose: Implements a name2name plugin that maps object IDs into filesystem-safe paths, distributing short IDs across hash-derived subdirectories and segmenting long IDs.

APIs and control flow: `XrdOucN2No2p` implements `lfn2pfn()`, `lfn2rfn()`, and `pfn2lfn()`. `lfn2pfn()` optionally prefixes a local root, then delegates to `pfn2lfn()` for object-path transformation. `pfn2lfn()` leaves absolute paths untouched, replaces embedded slashes with a configurable character, creates hash fanout for IDs within the max filename length, or splits longer IDs into `oidMax`-sized path components. The exported `XrdOucgetName2Name()` parses `-slash`, `-maxfnlen`, and an object-id prefix.

State and persistence: The mapper owns `lRoot` and `oidPfx`; no on-disk state is created. Mappings are deterministic and depend on `_PC_NAME_MAX`, prefix, and replacement character.

Dependencies and integration: Uses `XrdOucTokenizer`, `XrdOucHashVal2`, `XrdSysError`, and XRootD plugin version metadata.

Risks and test signals: Option parsing uses `strtol(..., 16)` for numeric fields, so decimal-looking inputs are interpreted as hex. Tests should cover absolute paths, slash replacement, short and long IDs, buffer limits, prefix normalization, and invalid options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2No2p.cc -->
