# sources/user-network-fs/nfs-utils/support/include/nfs/export.h

## Purpose
Defines nfsd export limits and `NFSEXP_*` flag values shared by user-space export code and kernel cache protocols.

## Important APIs, Types, and Functions
Provides client/path size limits, export option flag masks, old-kernel feature masks, transport security flags, and `NFSEXP_XPRTSEC_*` helpers.

## Control Flow
Export parsers, feature probes, pseudo-root code, and cache writers set/test these bits when building export entries and kernel upcall responses.

## State and Persistence Behavior
No state. Flags become persistent when written to etab or sent to kernel caches.

## Dependencies and Integration Points
Included through `nfs/nfs.h` and `nfslib.h`. Must align with Linux nfsd export flags.

## Risks and Edge Cases
Flag drift breaks export semantics. Reserved or old-feature masks need care when supporting older kernels.

## Test Signals
Test option parsing to flags, kernel feature filtering, transport security serialization, and old-kernel compatibility paths.
