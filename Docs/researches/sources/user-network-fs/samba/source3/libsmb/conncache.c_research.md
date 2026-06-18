# sources/user-network-fs/samba/source3/libsmb/conncache.c

## Purpose

This file implements a negative connection cache on top of Samba `gencache`. It records domain/server pairs that recently failed connection attempts so other processes avoid repeated expensive retries.

## Important APIs, Types, and Functions

Public APIs are `has_negative_conn_cache_entry()`, `add_failed_connection_entry()`, and `flush_negative_conn_cache_for_domain()`. Internal helpers `negative_conn_cache_keystr()`, `negative_conn_cache_valuestr()`, `negative_conn_cache_valuedecode()`, and `delete_matches()` encode keys, statuses, and flush callbacks.

## Control Flow

Keys are formatted as `NEG_CONN_CACHE/<domain>,<server>`, with null server mapped to an empty string. Failed non-OK statuses are encoded as hexadecimal `NT_STATUS_V()` values and stored until `time(NULL) + FAILED_CONNECTION_CACHE_TIMEOUT`. Lookup reads the key, decodes status, and reports an entry only when the decoded status is not OK. Flush builds a wildcard key for a domain and passes `delete_matches()` to `gencache_iterate()`.

## State and Persistence Behavior

State persists in the shared gencache backend, not process-local memory. This gives the negative cache cross-process behavior. Entries expire by timeout or explicit domain flush.

## Dependencies and Integration Points

The file depends on `lib/gencache.h`, NTSTATUS encoding helpers, Samba debug logging, and the global `FAILED_CONNECTION_CACHE_TIMEOUT`. Winbind and connection-management paths can use it before attempting server connections.

## Risks and Test Signals

Risks include domain names with delimiter characters producing ambiguous keys, value parse failures becoming internal-error cache hits, stale negative entries suppressing recovered servers until expiry, and wildcard flush matching more than intended. Tests should cover null domain/server inputs, OK statuses not being cached, decode failures, expiry behavior, exact server and domain-wide flush, and cross-process visibility through gencache.
