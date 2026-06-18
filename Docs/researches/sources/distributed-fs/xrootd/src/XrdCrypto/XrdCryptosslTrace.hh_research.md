<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslTrace.hh

## Purpose
Defines tracing macros for the cryptossl implementation and declares the global `sslTrace` pointer used by source files in this plugin.

## Important APIs, types, and functions
- `QTRACE(act)` checks whether `sslTrace` is set and whether the requested `cryptoTRACE_*` bit is enabled.
- `PRINT(y)`, `TRACE(act,x)`, `DEBUG(y)`, and `EPNAME(x)` wrap `XrdOucTrace` logging and endpoint names when `NODEBUG` is not defined.
- Under `NODEBUG`, macros compile to empty definitions.
- Declares `extern XrdOucTrace *sslTrace`.

## Control flow
At runtime, implementation files set an endpoint with `EPNAME`, then call `DEBUG`, `TRACE`, or `PRINT`. The macros route messages through `sslTrace->Beg(epname)`, stream to `std::cerr`, and call `sslTrace->End()`. `SetTrace()` in the factory configures the pointer and mask.

## State and persistence behavior
The header declares a process-global trace pointer; the definition is in `XrdCryptosslAux.cc`. Logging is transient except for whatever backend the `XrdSysError` logger writes to.

## Dependencies and integration points
Includes `XrdOucTrace.hh`, `XrdCryptoAux.hh`, and in debug builds `XrdSysHeaders.hh`. It relies on `cryptoTRACE_*` masks from generic crypto headers while the factory maps `sslTRACE_*` flags.

## Risks and edge cases
Macros assume an `epname` symbol exists for `PRINT`, so callers should use `EPNAME` in functions that log. In non-debug builds, `QTRACE(x)` expands to nothing, which may be unsafe if used in expression contexts. Global trace pointer access is not synchronized.

## Test signals
Build tests should cover debug and `NODEBUG` configurations. Runtime trace tests should call factory `SetTrace()` with notify/debug/dump masks and verify representative messages do not crash when `sslTrace` is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslTrace.hh -->
