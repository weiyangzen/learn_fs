<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPList.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPList.hh

Purpose: Provides a prefix path list that maps paths to flags or stores paired path/name metadata.

APIs and control flow: `XrdOucPList` stores a path, path length, attrs, and either flags or a name pointer via a union. `PathOK()` tests whether a candidate starts with the stored prefix. `Set(pd,pn)` stores path and name in one allocation. `XrdOucPListAnchor` offers longest-prefix `Find()`/`About()`, exact `Match()`, ordered `Insert()`, defaults for absolute and non-absolute paths, and list cleanup.

State and persistence: Entries own their `path` allocation; name mode stores `name` inside that allocation. The anchor holds defaults and an in-memory list only.

Dependencies and integration: Uses libc allocation and formatting. It is a configuration utility for path-prefix policies.

Risks and test signals: Prefix checks do not enforce component boundaries. The flags/name union means callers must know which constructor or setter was used. Tests should cover longest-prefix ordering, default selection, name storage, exact matching, and ownership cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPList.hh -->
