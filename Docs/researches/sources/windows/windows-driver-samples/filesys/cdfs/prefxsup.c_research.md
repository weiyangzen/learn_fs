# File Research: sources/windows/windows-driver-samples/filesys/cdfs/prefxsup.c

## Purpose

Maintains per-directory prefix lookup trees for fast path resolution. Each directory FCB owns exact-case and ignore-case splay-tree roots.

## Main Entry Points

- `CdInsertPrefix`
- `CdRemovePrefix`
- `CdFindPrefix`
- `CdFindNameLink`
- `CdInsertNameLink`

## Prefix Insertion and Removal

`CdInsertPrefix` inserts long-name or short-name prefix entries for an FCB under its parent. It allocates a `PREFIX_ENTRY` for short-name matches when needed, allocates a larger name buffer when the embedded buffer is too small, splits storage into exact-case and ignore-case names, and inserts the selected name into the parent’s matching splay tree.

`CdRemovePrefix` removes both short-name and long-name entries from the parent’s exact-case and ignore-case trees, clears in-tree flags, and frees any allocated long-name prefix buffer.

## Lookup

`CdFindPrefix` walks from a starting FCB through as many path components as are already present in prefix trees. It dissects the remaining path one component at a time, searches the appropriate splay tree, and descends to the matched child FCB. For ignore-case lookups, it copies the exact-case spelling back into the caller’s buffer. It carefully handles child acquisition failures by temporarily referencing the child, releasing the parent, then acquiring the child.

`CdFindNameLink` searches a splay tree using `CdFullCompareNames` and splays successful hits to the root.

`CdInsertNameLink` inserts a `NAME_LINK` into a splay tree and rejects duplicate names.

## Dependencies

Uses CDFS name comparison/dissection helpers, FCB resources and VCB reference accounting, RTL splay tree routines, and `PREFIX_ENTRY` fields embedded in FCBs.
