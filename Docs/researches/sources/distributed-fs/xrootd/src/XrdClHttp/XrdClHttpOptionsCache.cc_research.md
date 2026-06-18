# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOptionsCache.cc

## Purpose

This file implements the singleton lifecycle and expiry behavior for `VerbsCache`, the endpoint capability cache used to remember whether an HTTP endpoint supports WebDAV `PROPFIND`.

## Important APIs, types, and functions

Static storage is defined for `VerbsCache::g_cache`, `m_expiry_launch`, `m_shutdown_lock`, `m_shutdown_requested_cv`, `m_shutdown_requested`, `m_expire_tid`, and the shutdown trigger. `Instance` starts the background expiry thread exactly once unless shutdown is already underway. `ExpireThread` wakes every 30 seconds until shutdown and calls `g_cache.Expire`. `Expire` removes expired map entries. `Shutdown` sets the shutdown flag, notifies the expiry thread, and joins it if needed.

## Control flow

First use of `VerbsCache::Instance` launches `ExpireThread` with `std::call_once`. Consumers call header/OPTIONS paths to `Put` and `Get` entries defined inline in the header. At plugin/library shutdown, static `shutdown_s` invokes `Shutdown`, causing the worker thread to exit cleanly before static storage disappears.

## State and persistence behavior

All state is process-local and volatile. Known positive entries live for six hours, negative/unknown entries for fifteen minutes, and the background thread prunes expired entries. No endpoint capability information is persisted across process restarts.

## Dependencies and integration points

This implementation depends on C++ threading primitives and `curl/curl.h` inclusion. It is integrated by `CurlStatOp` and `CurlWorker` OPTIONS handling. Its shutdown timing matters because the HTTP plugin can be loaded and unloaded dynamically.

## Risks and edge cases

`Instance` returns `g_cache` even during shutdown, but suppresses launching a new expiry thread. Long-running users that call after shutdown could see stale entries without maintenance. Expiration is periodic and opportunistic; expired entries are also treated as misses by `Get`, so delayed cleanup should not affect correctness. Static destructor ordering remains a classic plugin-unload risk.

## Test signals

Tests should cover first-use thread launch, `Expire` removing stale entries, shutdown join behavior, and that `Instance` does not relaunch the thread after shutdown. No direct tests were found.
