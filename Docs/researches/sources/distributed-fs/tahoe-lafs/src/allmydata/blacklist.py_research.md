# sources/distributed-fs/tahoe-lafs/src/allmydata/blacklist.py

## Purpose

This module implements storage-index-based access prohibition. It loads a blacklist file mapping base32 storage indexes to reasons, checks objects against it, and wraps prohibited file nodes with an object that lists safely but fails on content operations.

## Important APIs, Types, And Functions

`FileProhibited` carries a human-readable reason. `Blacklist` owns `blacklist_fn`, `last_mtime`, and `entries`; `read_blacklist()` reloads on first use or newer mtime, and `check_storageindex(si)` returns a reason if blocked. `ProhibitedNode` implements `IFileNode` and delegates identity/query methods to a wrapped node while making size/check operations harmless and mutating/download operations raise `FileProhibited`.

## Control Flow

A client creates `Blacklist` from the configured `access.blacklist` path. Each check calls `read_blacklist()`, which clears entries if the file is missing/unreadable or reloads non-comment lines as `storage-index reason`. `check_storageindex()` logs prohibited hits and returns the reason to callers that can substitute `ProhibitedNode`.

## State And Persistence

The persistent state is the external blacklist file. In-memory state caches entries and last modification time. `ProhibitedNode` keeps a wrapped node and reason but does not persist anything.

## Dependencies And Integration Points

The module depends on Twisted logging, Zope interface declarations, `IFileNode`/`IFilesystemNode`, Tahoe base32 utilities, and output quoting. It integrates with `client.init_blacklist()` and node construction paths that apply blacklist decisions.

## Risks

Malformed blacklist lines or invalid base32 raise after logging, potentially preventing access checks rather than failing open. Reload is based on mtime greater-than only, so coarse timestamp filesystems or same-time rewrites can leave stale entries. Missing/unreadable blacklist clears entries and permits access. `ProhibitedNode.check()` and repair methods return `None`, which callers must handle as a non-distributed or unavailable result.

## Test Signals

Cover missing file, comments/blank lines, valid reload, malformed line/base32 failure, mtime updates, prohibited download/overwrite/read failures, and directory listing behavior that still exposes wrapped identity without content access.
