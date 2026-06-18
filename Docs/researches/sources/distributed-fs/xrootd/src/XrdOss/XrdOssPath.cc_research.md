# sources/distributed-fs/xrootd/src/XrdOss/XrdOssPath.cc

## Purpose
Implements cache path encoding/decoding helpers for XA cache spaces, old-style cache paths, suffix classification, cache-group extraction, PFN generation, and cache filename prefix initialization.

## Important APIs, types, and functions
`Convert()` converts an old symlink target into a new target by preserving the prefix before `%` and tamping slashes in the new path. `Extract()` reads a symlink or path and returns the cache group while trimming the buffer to the cache base. `genPath()` ensures a cache group directory exists in a path and builds a four-byte suffix encoding group-position and group-name length. `genPFN(fnInfo&, ...)` generates either old-style tamped PFNs or XA PFNs using a per-process prefix, two-level sequence directory, encoded sequence, and suffix. `genPFN(char*,...)` reverses a tamped path after `%`. `getCname()` extracts the cache group from a symlink. `pathType()` classifies migration/memory suffixes such as `.anew`, `.fail`, `.mmap`, and `.pfn`. `Trim2Base()` truncates extended cache paths to the allocation root. `InitPrefix()` seeds the PFN prefix from time, pid, and encoded network address. `posCname()` decodes cache-group position from the suffix.

## Control flow
Configuration calls `genPath()` and later `InitPrefix()` once cache FS mode is known. Allocation calls `genPFN()` for every cache target. Rename/relocate/accounting paths call `getCname()`, `Trim2Base()`, `Convert()`, and `pathType()` to interpret symlink targets and sidecar suffix files.

## State and persistence
Static `h2c`, `pfnPfx`, and suffix table are process-global. Generated PFN names and symlink targets are persistent filesystem artifacts. `genPFN()` uses a static mutex-protected sequence counter for uniqueness within one process, combined with the prefix for broader uniqueness.

## Dependencies and integration points
Depends on `XrdOssSpace` for space-name limits, `XrdNetUtils` for address encoding, and POSIX `lstat/readlink`. Tight coupling exists with `XrdOssCache` suffix fields and symlink layout assumptions in create/rename/relocate.

## Risks and test signals
Encoding is compact and easy to break. Tests should cover long group names, paths near `MAXPATHLEN`, missing `pfnPfx`, network-address encoding failure, suffix classification ranges, old-style tamped paths, XA symlink targets ending in `%`, and `Trim2Base()` on malformed input.
