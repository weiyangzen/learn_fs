<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.hh

## Purpose
Declares `XrdCryptosslFactory`, the concrete `XrdCryptoFactory` subclass for the OpenSSL provider. It is the main API surface through which the rest of XRootD requests cryptographic objects and helper hooks.

## Important APIs, types, and functions
- Defines `XrdCryptosslFactoryID` as `1` and declares provider class `XrdCryptosslFactory`.
- Declares trace control, KDF hook retrieval, cipher constructors, digest constructors, RSA constructors, X.509/CRL/request constructors, chain helper hooks, and proxy helper hooks.
- Defines `DebugON = 1` at header scope.

## Control flow
No implementation control flow exists in the header, but the method set mirrors the virtual factory contract. The implementation returns concrete objects or function pointers matching these declarations.

## State and persistence behavior
Instances inherit provider name/ID state from `XrdCryptoFactory`. The header itself declares no members. `DebugON` at header scope creates global state in every translation unit that includes it unless build/link behavior hides it.

## Dependencies and integration points
Includes `XrdCryptoFactory.hh` and `XrdSysPthread.hh`. It is consumed by the factory implementation and plugin loader-facing code. The hook return types are defined in the generic crypto factory headers.

## Risks and edge cases
The non-`extern` `int DebugON = 1;` in a header is a notable ODR/link risk in C++ and may rely on historical compiler/linker behavior. Broad virtual API exposure means any signature mismatch with generic factory typedefs breaks plugin integration.

## Test signals
Build tests with modern compilers and `-fno-common`-style strictness should catch multiple-definition problems. Interface tests should instantiate the factory via plugin symbol and ensure every declared virtual override is callable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.hh -->
