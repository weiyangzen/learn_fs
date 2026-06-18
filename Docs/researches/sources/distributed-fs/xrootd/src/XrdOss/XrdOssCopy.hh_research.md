# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCopy.hh

## Purpose
Declares the small static copy helper used by OSS relocation code.

## Important APIs, types, and functions
`XrdOssCopy::Copy(const char *inFn, const char *outFn, int outFD)` copies or links data from an input pathname into a caller-supplied destination fd/path pair and returns the copied size or a negative error. The private `Write()` helper writes a buffer at an offset and is implemented in the `.cc`.

## Control flow
There is no header control flow. The public API intentionally exposes only a static operation; no instance state is needed.

## State and persistence
The class has no data members. All persistence effects occur in the implementation by modifying the destination file, copying xattrs, and changing timestamps.

## Dependencies and integration points
Forward-only declaration avoids include dependencies. Included by `XrdOssReloc.cc` and `XrdOssCreate.cc` even though relocation is the direct data-copy caller in this subset.

## Risks and test signals
Callers must pass an already valid output fd and must expect `Copy()` to close it. Tests should check this ownership contract and negative return propagation.
