<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/share.h -->
# sources/user-network-fs/ksmbd-tools/include/management/share.h

## Purpose

Declares the share-management model and configuration keys for ksmbd shares.

## Important APIs, Types, and Functions

Defines `struct ksmbd_share`, user/host map enums, `KSMBD_SHARE_CONF` key enum, key/default arrays, helpers for global/broken config entries, flag helpers, lookup/refcount APIs, connection accounting, map lookups, iteration, and share-config response serialization.

## Control Flow

Config parsing creates shares from smbconf groups; mountd looks up shares for share-config and tree-connect requests; addshare uses the enum/default arrays to prompt and rewrite configuration.

## State and Persistence Behavior

State is an in-memory share table containing path, masks, force uid/gid, flags, veto list, guest account, user maps, host maps, comments, locks, reference counts, and connection counts. Persistence is via `ksmbd.conf` rewritten by addshare.

## Dependencies and Integration Points

Depends on GLib hash tables/locks and kernel response structures from ksmbd_server.h.

## Risks and Edge Cases

The enum order is an ABI-like contract for addshare descriptions and defaults. Host matching is noted as simplistic. Refcount and map-lock discipline are critical under concurrent worker processing.

## Test Signals

Tests should parse all share keys, validate name hashing/equality, map users/groups, enforce hosts allow/deny, open/close connection limits, and serialize share config payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/share.h -->
