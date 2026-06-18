# File Research: sources/os/linux/linux-stable/fs/hfsplus/bfind.c

## Scope

Implements HFS+ B-tree search cursors, exact/CNID-first binary-search strategies, record reads, relative record movement, and catalog record size validation.

## APIs And Behavior

- `hfs_find_init()` allocates paired search/current key buffers and locks the tree mutex with a tree-specific lock class.
- `hfs_find_exit()` drops the current bnode, frees key memory, unlocks the tree, and clears the cursor tree pointer.
- `hfs_find_1st_rec_by_cnid()` searches for the first record matching a CNID across extents, catalog, or attributes trees.
- `hfs_find_rec_by_key()` performs exact key comparison using the tree comparator.
- `__hfs_brec_find()` binary-searches within one bnode and fills record/key/entry offsets and lengths.
- `hfs_brec_find()` descends root-to-leaf through index nodes, validating height/type consistency.
- `hfs_brec_read()` finds and reads an entry into a bounded caller buffer.
- `hfs_brec_goto()` walks forward/backward across leaf sibling links and updates cursor offsets.
- `hfsplus_brec_read_cat()` reads a catalog record and validates that its length matches the record type, including variable-size thread records.

## State And Dependencies

The file depends on B-tree key comparators, bnode read helpers, record length/key-length helpers, and lock-class selection. It is the shared cursor layer for catalog, extents, attributes, and directory iteration.

## Risks And Invariants

Search cursors own the tree mutex. Callers that copy `struct hfs_find_data` must avoid double-freeing the shared key buffer and must explicitly drop secondary bnodes, as seen in rename paths. Catalog record size validation is a corruption hardening point for variable-length thread records.
