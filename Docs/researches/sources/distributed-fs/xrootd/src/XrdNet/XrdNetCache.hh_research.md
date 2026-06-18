## sources/distributed-fs/xrootd/src/XrdNet/XrdNetCache.hh

Purpose: Declares the DNS cache backing optional reverse-name caching for network addresses.

Important APIs and types: Public `Add`, `Find`, and static `SetKT` form the cache interface. Private `anItem` stores IPv4/IPv6 key bytes, hash, hostname, expiry, and chain pointer.

Control flow: Header-defined `anItem` constructors duplicate hostnames and compute expiration from constructor arguments; `operator!=` compares hash, length, and key bytes.

State and persistence: Owns a heap hash table and chained entries for process lifetime. Static `keepTime` defines default TTL. No durable persistence.

Dependencies and integration points: Uses `XrdSysMutex` and is referenced by `XrdNetAddrInfo` through a static pointer. Intended initialization is through `XrdNetAddr::SetCache`.

Risks: Destructor comment states deletion loses memory, so ordinary RAII expectations do not hold. `SetKT` is static and not locked. `Find` ownership convention requires callers to free returned strings.

Test signals: Header compatibility with `XrdNetAddrInfo`; static TTL setting before cache use; leak checks should account for intentional process-lifetime cache behavior.
