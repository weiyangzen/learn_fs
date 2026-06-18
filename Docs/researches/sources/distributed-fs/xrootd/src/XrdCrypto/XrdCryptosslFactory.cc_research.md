<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.cc

## Purpose
Implements the cryptossl plugin factory, initializing OpenSSL/TLS support and exposing OpenSSL-backed implementations for ciphers, message digests, RSA keys, X.509 certificates, CRLs, requests, chain helpers, and proxy/VOMS helpers through the generic `XrdCryptoFactory` API.

## Important APIs, types, and functions
- Static `Logger` and `eDest` back the cryptossl trace destination.
- `XrdCryptosslFactory::XrdCryptosslFactory()` calls `XrdTlsContext::Init()` and seeds OpenSSL RAND with `XrdSutRndm` bytes.
- `SetTrace()` creates/updates global `sslTrace` and maps `sslTRACE_*` flags to the trace mask.
- Constructor families return `XrdCryptosslCipher`, `XrdCryptosslMsgDigest`, `XrdCryptosslRSA`, `XrdCryptosslX509`, `XrdCryptosslX509Crl`, and `XrdCryptosslX509Req` after validity checks.
- Hook accessors return function pointers from `XrdCryptosslAux.cc` and `XrdCryptosslgsiAux.cc`.
- `XrdVERSIONINFO(XrdCryptosslFactoryObject,cryptossl)` and `extern "C" XrdCryptosslFactoryObject()` provide plugin entry/version symbols.

## Control flow
The factory singleton is lazily instantiated in `XrdCryptosslFactoryObject()`. Its constructor initializes TLS/OpenSSL process state and aborts on initialization failure. Each creation method allocates a concrete implementation, checks the relevant validity signal (`IsValid()` or `Opaque()`), returns the object on success, or deletes it and returns null on failure. Hook methods are simple function-pointer returns and let higher-level XRootD code invoke auxiliary operations without linking to concrete classes.

## State and persistence behavior
The factory is a static process-lifetime singleton. `SetTrace()` lazily allocates global `sslTrace`; it is not freed in this file. Factory-created objects own their OpenSSL state individually. The constructor seeds OpenSSL's process-global random state.

## Dependencies and integration points
Includes every cryptossl concrete header, OpenSSL `rand.h`/`ssl.h`, `XrdTlsContext`, `XrdSutRndm`, XRootD logging/tracing, and version macros. The factory object is the external plugin boundary and is identified as provider `"ssl"` with ID `1`.

## Risks and edge cases
The factory uses C-style downcasts in copy constructors (`*((XrdCryptosslCipher *)&c)` and RSA equivalent), so passing a non-cryptossl implementation through this factory is undefined behavior. The factory aborts the process if `XrdTlsContext::Init()` fails. `DebugON` is defined in the header, not here, which can cause multiple-definition risks if included in multiple translation units. Trace state is global and not synchronized beyond pointer assignment.

## Test signals
Plugin loading tests should verify `XrdCryptosslFactoryObject()` returns a stable singleton and version symbol. Factory tests should cover valid/invalid algorithm names, all constructor overloads, failure cleanup, trace mask mapping, and hook function pointer non-nullness. Cross-provider copy calls should be guarded or tested for expected rejection if the generic API allows them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.cc -->
