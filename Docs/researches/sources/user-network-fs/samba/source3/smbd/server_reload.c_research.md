# sources/user-network-fs/samba/source3/smbd/server_reload.c

## Purpose

`server_reload.c` handles runtime service/printer reloads for smbd. It detects changed configuration files, reloads `smb.conf` shares, refreshes socket options, invalidates caches, and manages auto-loaded printer shares from the persistent pcap cache populated by the background print process.

## Important APIs, Types, And Functions

- `snum_is_shared_printer()` identifies browseable, valid, printable services.
- `delete_and_reload_printers()` reloads printer services from pcap state and removes stale auto-loaded printer shares not currently used.
- `reload_services()` reloads the active services file and share definitions, kills unused services, reopens logs, refreshes interfaces, reapplies socket options to active SMBX connections, and resets name-mangling and free-space caches.
- Static state `reload_last_pcap_time` suppresses duplicate printer reloads when the pcap cache has not changed.

## Control Flow

Printer reload first checks `load printers`, creates a stack frame, validates that pcap cache is loaded, compares pcap timestamp against `reload_last_pcap_time`, calls `load_printers()`, iterates existing services, skips the special `printers` service and non-printer services, and kills stale auto-loaded printer services when the printer name no longer exists and no connection uses that service. It then calls `load_printers()` again to ensure deleted printers are gone.

`reload_services()` checks for `include`/next-config changes through `lp_next_configfile()`, updates the dynamic config path if needed, reopens logs, short-circuits test reloads when the file list has not changed, kills unused services, loads config with shares, recursively retests when the config path was not a test reload, reopens logs again, reloads interfaces, reapplies keepalive and configured socket options to each active connection, and flushes mangle/free-space caches.

## State And Persistence Behavior

This file changes in-memory loadparm service tables, dynamic config filename state, printer service state, interface lists, socket options, and process caches. It does not directly persist config, but it consumes persistent pcap cache metadata and affects whether auto-loaded printer service definitions remain present. The `reload_last_pcap_time` static timestamp is per-process state, so each smbd can independently decide whether pcap-backed printer inventory changed.

## Dependencies And Integration Points

Dependencies include loadparm, pcap cache, printer list/load APIs, connection service-use checks, logging, interface loading, socket option setters, mangle cache, and dfree cache. Parent and child smbd processes call `reload_services()` from SIGHUP or `MSG_SMB_CONF_UPDATED` paths, while printer enumeration or pcap callbacks call `delete_and_reload_printers()`.

## Risks

Reload behavior must avoid removing services still in use; `connections_snum_used()` is the guard for printer services. Recursive `reload_services(..., true)` after a non-test load depends on `lp_file_list_changed()` to prevent unnecessary work. Socket option application assumes active connection sockets remain valid. Printer cache timestamp handling can skip reloads if the pcap producer fails to update time correctly.

## Test Signals

Test signals include SIGHUP/config-update reloads, included config-file path changes, unchanged test reload short-circuit, stale auto-loaded printer removal, active printer service preservation, socket option refresh on existing connections, and cache invalidation after share changes. Printer tests should cover disabled `load printers` and missing pcap cache.
