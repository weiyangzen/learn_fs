# File Research: sources/os/linux/linux/fs/hfsplus/bfind.c

Purpose: Implements HFS+ B-tree search cursor lifecycle, binary record search strategies, leaf traversal, record reading, and typed catalog record validation.

Key functions:
- `hfs_find_init()` allocates search/current key buffers and locks the B-tree mutex using the tree-specific subclass.
- `hfs_find_exit()` releases the current node, frees keys, and unlocks the tree.
- `hfs_find_1st_rec_by_cnid()` finds the first record matching a CNID in extents, catalog, or attributes trees.
- `hfs_find_rec_by_key()` compares full keys using the tree comparator.
- `__hfs_brec_find()` binary-searches one node and populates offsets/lengths.
- `hfs_brec_find()` descends root-to-leaf through index records, validating node height and type.
- `hfs_brec_read()` reads a record by key.
- `hfs_brec_goto()` moves forward/backward across leaf sibling chains.
- `hfsplus_brec_read_cat()` validates catalog record sizes based on type, including variable-length thread records.

Dependencies and integration:
- Shared by attributes, catalog, extents, and directory code.
- Uses `hfs_brec_keylen()`/`hfs_brec_lenoff()` from `brec.c` and B-node I/O from `bnode.c`.

Risk notes:
- `hfs_brec_find()` returns best-fit state even for `-ENOENT`, which insert callers depend on.
- Typed catalog validation is important defense against malformed on-disk records.
