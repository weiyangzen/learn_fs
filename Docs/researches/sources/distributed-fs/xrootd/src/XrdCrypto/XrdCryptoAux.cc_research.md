# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoAux.cc

## Purpose

`XrdCryptoAux.cc` implements common crypto tracing setup and timezone correction helpers shared by the abstract crypto layer and plugins.

## Important APIs and Functions

`XrdCryptoSetTrace(kXR_int32 trace)` initializes a static logger/error destination, lazily creates global `cryptoTrace`, and maps notification/debug/dump flags to `cryptoTrace->What`. `XrdCryptoTZCorr()` computes and caches the local timezone offset relative to UTC using `localtime_r`, `gmtime_r`, and `mktime`.

## Control Flow

Trace setup always resets the trace mask before enabling progressively more verbose categories. Timezone correction computes once on first successful call and returns the cached offset thereafter.

## State and Persistence Behavior

Static process state includes `Logger`, `eDest`, global `cryptoTrace`, `TZCorr`, and `TZInitialized`. The trace object persists for the life of the process. Timezone offset assumes no daylight-saving correction changes after initialization.

## Dependencies and Integration Points

It depends on `XrdSysLogger`, `XrdSysError`, `XrdCryptoAux.hh`, and `XrdCryptoTrace.hh`. The global `cryptoTrace` is consumed by trace macros in the crypto subsystem.

## Risks and Edge Cases

Trace initialization is not synchronized, so concurrent first calls can race. `XrdCryptoTZCorr()` caches offset and ignores later timezone/DST changes. The comment says no DST; callers must not use it for precise civil-time conversion across DST transitions.

## Test Signals

Tests should verify trace flag mapping, idempotent repeated calls, and timezone correction under controlled `TZ` settings. Thread-safety tests would expose first-call races.
