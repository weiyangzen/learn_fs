# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPList.cc

Purpose: implements the mutable path-prefix list used by CMS cache/path ownership tracking. The list is sorted by decreasing path length so longest-prefix matches win for `Find()` and `Type()`, and so mask propagation can handle subpaths before parent paths.

Important APIs/functions: `XrdCmsPList_Anchor::Add()` inserts a unique path without mask inheritance; `Find()` returns the first prefix match into an `XrdCmsPInfo`; `Insert()` merges read-only/read-write/staging masks for an advertised path and adjusts subset/superset masks; `Remove()` clears a server mask from all entries and deletes empty entries; `Type()` reports `w`, `r`, or `?`; `XrdCmsPList::PType()` returns `w`, `r`, `ws`, or `rs`.

Control flow: all public anchor mutations lock the anchor mutex, traverse the singly linked list, and unlock before returning. `Insert()` first walks entries with length greater than or equal to the new path, merging incoming masks into subset entries, then either updates the exact path or creates a new node and inherits masks from matching shorter parent prefixes.

State and persistence: state is in-memory only: linked `XrdCmsPList` nodes with duplicated path strings and `XrdCmsPInfo` bitmasks. There is no disk persistence; path state is rebuilt from logins/configuration and removed by server mask.

Dependencies/integration: uses `SMask_t` from `XrdCmsTypes.hh` and `XrdSysMutex`. It is used through `Cache.Paths` by protocol admission and forwarding (`XrdCmsProtocol::AddPath`, `ConfigCheck`, `Reissue`) to determine which servers handle a path.

Risks: prefix matching uses raw `strncmp` over path length, so callers must normalize paths and avoid ambiguous prefixes such as `/a` matching `/abc` unless that is an accepted CMS convention. `new XrdCmsPList` is unchecked. `First()` exposes the list without locking, so callers need external discipline. Misspelling in comments is harmless.

Test signals: exercise insertion order, duplicate `Add()`, exact/superset/subset mask merging, `Remove()` deleting empty entries, and longest-prefix `Find()` behavior with read-only, read-write, and staging masks.
