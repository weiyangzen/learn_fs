# sources/user-network-fs/nfs-ganesha/src/include/nfs_ip_stats.h

## Purpose

`nfs_ip_stats.h` declares the IP-address-to-hostname cache used for client-name diagnostics and possibly access/logging paths.

## Important APIs, Types, and Functions

Constants define return values (`IP_NAME_SUCCESS`, `IP_NAME_INSERT_MALLOC_ERROR`, `IP_NAME_NOT_FOUND`) and `IP_NAME_PREALLOC_SIZE`. `nfs_ip_name_t` stores a timestamp followed by a flexible hostname string. APIs are `nfs_ip_name_get`, `nfs_ip_name_add`, and `nfs_ip_name_remove`.

## Control Flow

Callers look up a `sockaddr_t` in the cache, add successful reverse-resolution results with a hostname and size, and remove entries when invalidating or updating names.

## State and Persistence Behavior

State is in-memory hashtable entries with timestamps and variable-size hostnames. No durable persistence is declared; stale entries depend on implementation TTL or explicit removal.

## Dependencies and Integration Points

It depends on `hashtable.h`, network address types from surrounding includes, and hostname limits from `<netdb.h>`. It integrates with `nfs_Init_ip_name`, logging, client manager, and address utilities.

## Risks and Test Signals

Risks include missing direct include for `sockaddr_t` if included standalone, hostname buffer size errors, stale reverse DNS, timestamp overflow/TTL bugs, and allocation failure handling. Tests should add/get/remove IPv4 and IPv6 names, handle oversized hostnames, simulate allocation failure, validate timestamp aging, and stress concurrent lookups if the implementation is shared.
