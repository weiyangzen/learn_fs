# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMark.hh

## Purpose
`XrdNetPMark.hh` defines the abstract packet-marking interface used by XRootD protocols to attach SciTags/Firefly metadata to TCP flows. It separates mark discovery (`Begin()` from an authenticated `XrdSecEntity`) from mark propagation (`Begin()` from a peer address plus an existing handle) and exposes shared experiment/activity ID validation rules.

## Important APIs, Types, and Functions
`XrdNetPMark` is a non-owning service interface whose destructor notes that the service object cannot be deleted by callers. The nested `Handle` owns an application name string plus experiment and activity codes; `getEA(int&, int&)` returns valid codes, while `Valid()` accepts either the special HTTP-TPC zero/zero value or encoded values derived from the SciTags total ID range. Static `getEA(const char*, int&, int&)` parses CGI strings in the implementation file.

## Control Flow and State
Protocol code creates handles through `Begin()`, stores them for the lifetime of a marked transfer, and deletes the handle to end reporting. `Handle` state is simple heap-owned C string plus two integers. Copy construction duplicates `appName`, allowing derived handles such as `XrdNetPMarkFF` to preserve the base code values.

## Dependencies and Integration Points
The header forward-declares `XrdNetAddrInfo` and `XrdSecEntity`. `XrdNetPMarkCfg` implements the interface, xrootd/http/TPC modules consume it, and `XrdNetPMarkFF` derives from `Handle`.

## Risks and Test Signals
Risk centers on lifetime ownership and validity semantics: callers must delete returned handles but not the service object, and zero/zero is deliberately valid. Tests should cover CGI parsing, boundary values 65 and 65535, invalid total IDs that intentionally map to zero/zero when parsed, copy/destructor ownership, and protocol paths that pass handles between streams.
