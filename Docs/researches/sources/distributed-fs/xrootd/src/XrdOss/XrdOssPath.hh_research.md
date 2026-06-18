# sources/distributed-fs/xrootd/src/XrdOss/XrdOssPath.hh

## Purpose
Declares the static path utility interface and suffix constants used throughout OSS cache-space code.

## Important APIs, types, and functions
`fnInfo` packages allocation-root path, path length, generated slash position, and XA suffix pointer for `genPFN()`. `xChar` is `%`, the escape/sentinel character used in cache symlinks and suffix encodings. `sfxLen` is four bytes. Public static helpers include `Convert()`, `Extract()`, `genPath()`, `genPFN()` overloads, `getCname()`, `isXA()`, `InitPrefix()`, `pathType()`, and `Trim2Base()`. `theSfx` enumerates base, migration, memory, and PFN suffix types. `chkMem`, `chkMig`, `chkPfn`, and `chkAll` select suffix classification ranges.

## Control flow
No header execution. The declaration shapes call flow across cache construction, allocation, rename, relocation, stat/open path handling, and cleanup of sidecar migration/memory files.

## State and persistence
Declares static `h2c` and `pfnPfx`. These are initialized in the `.cc` and influence persistent PFN names.

## Dependencies and integration points
Includes only basic system headers through implementation users. It is included by cache, create, rename, relocate, and config files, making it the central contract for cache path layout.

## Risks and test signals
Public APIs operate on caller-provided buffers and raw C strings. Tests should verify buffer length failures, exact suffix enum ordering, `isXA()` behavior on empty/short strings, and consistency between `genPath()` suffix production and `posCname()` decoding.
