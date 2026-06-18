# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAtomics.cc

## Purpose
Provides the out-of-line error text helper for `XrdSsiMutex` construction failures.

## Important APIs, Types, And Functions
- `XrdSsiMutex::Errno2Text(int ecode)` returns `XrdSysE2T(ecode)`.

## Control Flow
When `XrdSsiMutex` construction fails in the header-defined constructor, it throws the result of `Errno2Text(rc)`. This file supplies the private member implementation.

## State And Persistence
No local state or persistence.

## Dependencies And Integration Points
Includes `XrdSsiAtomics.hh` and `XrdSysE2T.hh`. It links the header-only mutex wrapper to XRootD errno-to-text formatting.

## Risks And Edge Cases
The thrown pointer references text owned by `XrdSysE2T()` semantics. Callers catching exceptions should treat it as a message pointer, not owned storage.

## Test Signals
Compile/link tests should ensure `XrdSsiMutex` construction references resolve. Fault-injection tests can force `pthread_mutex_init` failures and verify a non-null message is thrown.
