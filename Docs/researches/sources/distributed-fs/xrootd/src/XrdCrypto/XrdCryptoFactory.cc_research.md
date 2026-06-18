# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoFactory.cc

## Purpose

`XrdCryptoFactory.cc` implements the abstract crypto factory defaults and the runtime plugin loader that locates concrete factories such as OpenSSL-backed `XrdCryptossl`.

## Important APIs and Functions

The constructor stores a truncated factory name and ID. Almost all virtual construction/hook methods (`Cipher`, `MsgDigest`, `RSA`, `X509`, CRL/REQ constructors, verification/parsing/export hooks, proxy hooks, KDF hooks, and trace setup) are abstract stubs. `operator==` compares factory names. `GetCryptoFactory(const char *factoryid)` is the substantive method: it validates the name, checks a static factory cache, records failed attempts, loads `libXrdCrypto<factoryid>.so` with `XrdOucPinLoader`, resolves `XrdCrypto<factoryid>FactoryObject`, calls it, and caches the returned factory.

## Control Flow

`GetCryptoFactory()` runs under a static mutex. For a new factory ID it grows a static `FactoryEntry` array, initializes a failed-status entry, creates or reuses a pinned loader from a static hash, resolves the factory-object creator, invokes it, then marks the entry successful. Subsequent calls return the cached factory or immediately fail if the prior attempt failed.

## State and Persistence Behavior

The loader cache, factory array, and factory objects are static process-lifetime state. Plugins are pinned through `XrdOucPinLoader`, so shared libraries remain loaded. Failed load attempts are remembered and suppress retry.

## Dependencies and Integration Points

It depends on dynamic loading, `XrdOucHash`, `XrdOucPinLoader`, `XrdSysMutex`, version metadata, and crypto trace macros. The plugin symbol and library naming must match CMake/install output and concrete plugin code.

## Risks and Edge Cases

`factoryname` has a fixed 10-byte buffer but `strcpy(newfactorylist[i].factoryname, factoryid)` copies unbounded input into it, so long factory IDs can overflow. Failed attempts are cached forever, which prevents recovery if a plugin appears later. If `plugins.Add()` stores a null loader after allocation failure, later lookups may behave unexpectedly. Stub methods return null/failure, so using the base factory directly is a runtime error.

## Test Signals

Tests should cover null/empty IDs, overlong IDs, successful plugin load, missing library, missing symbol, failed factory creation, repeated successful lookups, repeated failed lookups, and concurrent first loads.
