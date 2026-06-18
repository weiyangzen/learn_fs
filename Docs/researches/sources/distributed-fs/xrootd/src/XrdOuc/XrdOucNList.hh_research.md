<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.hh

Purpose: Declares linked-list utilities for matching names or wildcard patterns to integer flags.

APIs and control flow: `XrdOucNList` exposes flag access, next traversal, `NameOK()`, `NameKO()`, and `Set()`. `XrdOucNList_Anchor` adds mutex-protected `Insert()`, `Replace()`, `Find()`, `Pop()`, `Empty()`, and list swapping helpers.

State and persistence: Entries store a duplicated pattern split into left/right pieces plus an integer flag. The anchor owns list topology and a mutex; no serialization is provided.

Dependencies and integration: Includes pthread wrappers and platform string compatibility. It is a small infrastructure type for configuration-derived pattern lists.

Risks and test signals: `First()` returns the raw list without locking, and `Swap()` requires manual external locking. Tests should focus on caller locking discipline, pop/empty ownership, wildcard matching, and platform case-comparison behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.hh -->
