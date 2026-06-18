# File Research: sources/windows/reactos/drivers/filesystems/cdfs/prefxsup.c

Implements per-directory prefix/name caches for CDFS FCBs using exact-case and case-insensitive splay trees.

Key entry points:
- `CdInsertPrefix()` inserts an FCB name, and optionally a short-name prefix, into the parent directory's exact or ignore-case tree.
- `CdRemovePrefix()` removes long-name and short-name prefix entries from the parent trees and frees any allocated long-name buffer.
- `CdFindPrefix()` walks component-by-component from a starting directory FCB, following the longest cached prefix while acquiring child FCBs and releasing parents.
- `CdFindNameLink()` searches and splays a tree around a matching `NAME_LINK`.
- `CdInsertNameLink()` inserts a `NAME_LINK` into the ordered splay tree, ignoring duplicates.

Core mechanics:
- Each directory FCB owns `ExactCaseRoot` and `IgnoreCaseRoot` splay roots.
- A `PREFIX_ENTRY` stores both exact-case and ignore-case names, sharing either an embedded buffer or one allocated buffer split into two halves.
- Short-name entries are allocated lazily as a separate `PREFIX_ENTRY`.
- `CdFindPrefix()` updates the caller's remaining path and, on ignore-case lookup, copies exact-case spelling back into the caller's buffer.
- Child acquisition first tries nonblocking; if it cannot acquire and waiting is allowed, it temporarily references the child, drops the parent, then acquires the child.

Important invariants:
- Prefix entry insertion/removal assumes the parent FCB relationship is stable.
- Duplicate case-insensitive inserts are harmlessly ignored by `CdInsertNameLink()`.
- `CdFindPrefix()` returns with only the lowest matched FCB acquired.
- Teardown recursion is avoided elsewhere, but prefix removal must remain synchronized with FCB tree teardown.

Filesystem relevance:
- Speeds path resolution by caching already discovered child FCB names under their parent directory.
- Preserves exact-case name spelling for case-insensitive opens.

Notable risks:
- Allocation failure in `CdInsertPrefix()` quietly skips cache insertion rather than failing the open.
- Buffer ownership is split between embedded and allocated storage; freeing depends on pointer comparison against the embedded buffer.
