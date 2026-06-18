# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirHelper.cc

## Purpose

This file implements the process-wide adapter around `XrdXrootdRedirPI`. It centralizes plugin invocation, host/CGI or URL parsing, target network-address caching, TTL refresh, and conversion of plugin string replies into `Outcome`.

## Important APIs, types, and functions

`Init()` stores the plugin, logger, and IP hold time. `IsActive()` reports whether a plugin exists. `Redirect()` handles host and URL redirect forms. `ParseURL()` splits `scheme://host[:port][/tail]`. `SetClockForTesting()` replaces the clock for cache tests. Internal `LookupTarget()` owns a static `std::map` of `netInfo` entries with `XrdNetAddr`, expiry, mutex, and atomic refs.

## Control flow

For host-form redirects (`port >= 0`), `Redirect()` validates the port, splits `host?cgi`, resolves/caches the target address, calls `plugin->Redirect()`, and commits a rewritten port only when the plugin returns a replacement. For URL-form redirects (`port < 0`), it parses URL components, resolves the host, calls `RedirectURL()`, and leaves the negative option value unchanged. Empty plugin replies map to `Unchanged`, `!message` maps to `Error`, and other strings map to `Replaced`.

## State and persistence behavior

State is static and in-memory only: the plugin/logger pointers, TTL, test clock, and unbounded target-address cache. Cache entries are immortal once inserted, refresh after `gIPHold`, and keep the previous good address if refresh fails.

## Dependencies and integration points

The file depends on `XrdNetAddr`, `XrdNetAddrInfo`, private utility `splitHostCgi`, logger and mutex/atomic helpers, and `XrdXrootdRedirPI`. It is called from xroot redirect execution and shared with HTTP TPC redirect logic.

## Risks and edge cases

`Init()` writes globals without locking and assumes it runs before workers call `Redirect()`. The cache is intentionally unbounded; acceptable for a small redirect-target set but risky if targets are attacker-controlled. URL parsing is simple and does not fully handle IPv6 bracket semantics or malformed authorities. On first DNS failure, redirects silently remain unchanged except for logs.

## Test signals

Tests should cover host CGI splitting, port range validation, URL parse success/failure, empty/replacement/error plugin replies, port rewrite semantics, DNS failure fallback, TTL refresh, stale-address reuse on refresh failure, and test-clock restoration.
