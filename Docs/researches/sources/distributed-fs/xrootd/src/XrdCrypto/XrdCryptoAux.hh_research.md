# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoAux.hh

## Purpose

`XrdCryptoAux.hh` provides shared crypto macros, tracing flags, RSA defaults, key-derivation function typedefs, and utility declarations used across the XRootD crypto abstraction.

## Important APIs and Types

`ABSTRACTMETHOD(x)` logs that a virtual method must be overridden. Trace flags are `cryptoTRACE_Notify`, `cryptoTRACE_Debug`, `cryptoTRACE_Dump`, and `cryptoTRACE_ALL`. RSA constants enforce/default to 2048-bit keys and exponent `0x10001`. `XrdCryptoKDFunLen_t` and `XrdCryptoKDFun_t` define plugin KDF hooks. Declarations include `XrdCryptoKDFunLen()`, `XrdCryptoKDFun()`, `XrdCryptoSetTrace()`, and `XrdCryptoTZCorr()`.

## Control Flow

The header supplies declarations and macros only. Runtime behavior comes from concrete functions and plugin overrides.

## State and Persistence Behavior

No state is declared here except constants. Implementations use the trace and timezone declarations for process-global behavior.

## Dependencies and Integration Points

It includes C stdio/time, `XrdSysHeaders` on non-Windows, and `XProtocol/XProtocol.hh`. Almost all crypto base classes depend on this header for abstract-method diagnostics and constants.

## Risks and Edge Cases

`ABSTRACTMETHOD` writes to `std::cerr` but this header does not directly include `<iostream>`; it relies on transitive includes. Default RSA parameters are policy-bearing constants and should be updated cautiously.

## Test Signals

Compile tests should include this header independently across supported platforms. Policy tests should assert RSA defaults meet current security expectations.
