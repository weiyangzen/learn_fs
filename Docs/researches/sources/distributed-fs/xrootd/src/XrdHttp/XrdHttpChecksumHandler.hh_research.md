## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksumHandler.hh

Purpose: declares the implementation and public wrapper for HTTP checksum negotiation.

Important APIs/types: `XrdHttpChecksumHandlerImpl` owns configuration logic and exposes raw checksum pointers for selected algorithms, non-IANA configured names, and testing visibility into configured checksums. `XrdHttpChecksumHandler` is a thin facade forwarding `configure()`, `getChecksumToRunWantDigest()`, `getChecksumToRunWantReprDigest()`, and `getNonIANAConfiguredCksums()` to its implementation member.

State and persistence: the implementation combines static supported-checksum maps with per-instance configured checksum raw pointers. The raw pointers are valid as long as the static map contents remain alive and stable.

Dependencies and integration: includes checksum metadata and standard containers. The facade is likely embedded in the HTTP protocol/request handling layer.

Risks and test signals: exposing raw pointers to objects owned by a static map makes map reinitialization and concurrency important. Unit tests should exercise configure-before-use, no-compatible-checksum behavior returning `nullptr`, preference selection, and multiple handler instances.
