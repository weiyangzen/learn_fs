# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsFAttr.hh

## Purpose
Defines request and result structures for SFS extended file attribute operations routed through `XrdSfsFileSystem::FAttr()`.

## Important APIs, Types, And Functions
- `XrdSfsFAInfo` describes one attribute name, value, aligned value length, name length, and per-entry return code.
- `XrdSfsFABuff` is a linked buffer used for additional allocated attribute data.
- `XrdSfsFACtl` is the main control block, carrying logical/physical paths, CGI, environment pointer, namespace prefix, request type, options, and an array of `XrdSfsFAInfo`.
- `XrdSfsFACtl::RQST` values are `faDel`, `faGet`, `faLst`, `faSet`, and `faFence`.
- Options include `accChk`, `newAtr`, `xplode`, `retvsz`, and `retval`.

## Control Flow
Callers construct `XrdSfsFACtl` with a path, opaque CGI, and attribute count, then a filesystem implementation interprets `rqst` and `opts`. The destructor frees linked buffers and deletes the `info` array, making it the ownership boundary for allocations recorded in the control block.

## State And Persistence
The structure is request-scoped. It can point at logical and physical paths and may carry allocated buffers for returned attribute lists or values. Actual xattr persistence is delegated to filesystem implementations.

## Dependencies And Integration Points
Forward-depends on `XrdOucEnv`. Included by the SFS interface where `FAttr()` is declared. It bridges protocol-level xattr commands and physical filesystem/plugin-specific xattr operations.

## Risks And Edge Cases
Ownership is mixed: `XrdSfsFACtl` frees `fabP` and `info`, but not path strings, values, or environment pointers unless stored in those buffers. Implementations must set `VLen`, `NLen`, and `faRC` consistently for list expansion and return-value modes.

## Test Signals
Tests should cover construction/destruction with zero and multiple attributes, list expansion with `xplode`, return-size versus return-value modes, per-attribute error codes, and namespace-prefix handling.
