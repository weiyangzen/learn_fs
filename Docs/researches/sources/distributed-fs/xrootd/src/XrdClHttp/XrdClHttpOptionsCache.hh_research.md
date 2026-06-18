# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOptionsCache.hh

## Purpose

This header defines `XrdClHttp::VerbsCache`, a thread-safe process-wide cache mapping URL authorities to discovered HTTP verb capabilities, currently focused on whether `PROPFIND` is available.

## Important APIs, types, and functions

`HttpVerb` is a bitmask enum with `kUnset`, `kUnknown`, and `kPROPFIND`. `HttpVerbs` wraps bit operations and `IsSet`. `Put` normalizes a URL to an authority key, sets positive entries for six hours and unknown entries for fifteen minutes, and avoids overwriting known entries with unknown results. `Get` returns cached verbs when present and unexpired while counting hit/miss atomics. `GetUrlKey` extracts `scheme://authority`, stripping user-info if present. `Expire`, `Instance`, `ExpireThread`, and `Shutdown` are implemented in the `.cc`.

## Control flow

Stat operations call `Get` before choosing HEAD versus PROPFIND. If the result is unset, the worker inserts an OPTIONS operation. `HeaderParser` parses `Allow` headers into `HttpVerbs`, and `CurlOptionsOp` stores them with `Put`. Redirects repeat this process for the redirected authority.

## State and persistence behavior

`m_verbs_map` is guarded by a `shared_mutex`, hit/miss counts are atomic, and cache entries expire based on steady-clock deadlines. The key deliberately ignores path and query; capabilities are assumed authority-wide. State is not durable.

## Dependencies and integration points

The cache is included by operation, utility, and factory code. It uses heterogeneous lookup for `std::string`/`std::string_view` on C++20 and falls back to allocating a string on older standards.

## Risks and edge cases

Authority-level caching can be wrong for servers that vary WebDAV support by path. `GetUrlKey` returns an empty view for malformed URLs, so malformed inputs can collide in the cache if stored. The `GetVerbString` switch has no fallback return outside enum cases, which can warn or become undefined for invalid enum values. User-info stripping changes the key, which is desired for credentials but means two credentialed URLs share one capability entry.

## Test signals

Useful tests include key extraction with credentials, ports, no path, malformed URLs, positive versus unknown overwrite rules, expiration, hit/miss counters, and C++ standard-specific heterogeneous lookup behavior. No dedicated tests were found.
