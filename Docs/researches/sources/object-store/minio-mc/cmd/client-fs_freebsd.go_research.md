# sources/object-store/minio-mc/cmd/client-fs_freebsd.go

## Purpose

This FreeBSD platform file provides notify event constants and extended-attribute enumeration for the filesystem client. It mirrors the non-Linux Unix behavior where get/access notifications are unavailable.

## Important APIs, Control Flow, And State

`EventTypePut` includes create, write, and rename; `EventTypeDelete` includes remove; `EventTypeGet` is empty. `IsPutEvent` scans the configured put events for bit overlap, `IsDeleteEvent` checks remove, and `IsGetEvent` returns false. `getXAttr` converts an xattr byte value to string, and `getAllXattrs` lists all keys and fetches values while treating unsupported xattrs as nonfatal.

## Dependencies, Integration, Risks, And Tests

The file depends on `notify` and `xattr`, and integrates with `fsClient.Watch`, `fsClient.Get`, and `fsClient.Stat`. Persistent state is only whatever xattrs already exist on disk; this file does not mutate them. Risks are the absence of read-event support and brittle behavior if an xattr disappears between `List` and `Get`. Coverage is indirect through shared filesystem tests and any platform-specific build/test lane.
