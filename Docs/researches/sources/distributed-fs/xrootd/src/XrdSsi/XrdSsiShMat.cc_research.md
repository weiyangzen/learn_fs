# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMat.cc

## Purpose
`XrdSsiShMat.cc` implements the factory for shared-memory table backends.

## Important APIs and Functions
`XrdSsiShMat::New(NewParms&)` fills in a default implementation name of `"XrdSsiShMam"` when none is provided, constructs `XrdSsiShMam` for that implementation, and returns `0` with `errno = ENOTSUP` for unsupported implementation names.

## Control Flow
The factory mutates `parms.impl` when nil, performs a string comparison, and returns a newly allocated backend object. There is no plugin loading in this implementation; adding backends requires extending this file.

## State and Persistence
The factory itself stores no state and persists nothing. The returned backend owns its mapping state and backing-file persistence.

## Dependencies and Integration Points
It depends on `XrdSsiShMat.hh` and `XrdSsiShMam.hh`. `XrdSsi::ShMap<T>` calls this factory during create/attach.

## Risks and Test Signals
Tests should cover null implementation defaulting, explicit `"XrdSsiShMam"`, unsupported implementation error propagation, and caller cleanup when allocation fails.
