# File Research: sources/local-fs/reiserfsprogs/fsck/pass1.c

`pass1.c` implements pass 1 of rebuild-tree: it takes leaf blocks discovered by pass 0 and tries to insert whole leaves into a newly built tree.

Key responsibilities:
- Creates the new on-disk bitmap model, initially marking block 0, pre-super blocks, superblock, bitmap blocks, journal/reserved area, and bad blocks as used.
- Creates an “uninsertable leaves” bitmap where cleared bits represent leaves that pass 1 could not safely attach as whole nodes.
- Builds an allocable-block bitmap from blocks that are neither metadata nor found leaves nor referenced unformatted data.
- Initializes the block allocator/deallocator hooks used by tree balancing.
- Corrects pass-1 leaf contents before insertion:
  - Deletes directory entries hashed with the wrong hash function.
  - Enforces increasing directory entry hash offsets.
  - Zeroes indirect pointers that point to recovered leaves.
  - Keeps only one reference to multiply referenced unformatted blocks.
- Attempts whole-leaf insertion by comparing the candidate leaf’s first/last key against the existing tree position and neighbor delimiting keys.
- Marks successfully inserted leaf items unreachable initially, so the later semantic pass can mark truly reachable objects.
- Marks data blocks referenced by accepted indirect items as used in the new bitmap.
- Persists pass-1 state: new on-disk bitmap, uninsertables bitmap, and allocable bitmap.

Important exported helpers:
- `make_buffer()`
- `is_item_reachable()`
- `mark_item_unreachable()`
- `mark_item_reachable()`
- `remove_saved_item()`
- `load_pass_1_result()`
- `pass_1()`

Dependencies and data flow:
- Consumes `leaves_bitmap`, good/bad unformatted bitmaps, and pointer validation from pass 0.
- Produces `fsck_new_bitmap(fs)`, `fsck_uninsertables(fs)`, and `fsck_allocable_bitmap(fs)` for pass 2.
- Uses tree search, `fix_nodes()`, and `do_balance()` to attach leaf pointers into internal nodes.

Notable behavior:
- Pass 1 only inserts whole leaves when they do not overlap existing keys and cannot be merged with neighbors in a way that would violate balancing expectations.
- Leaves that are malformed, overlap existing tree contents, fall into journal special cases, or cannot satisfy neighbor conditions are deferred to pass 2.
- Duplicate unformatted pointers are resolved by preserving the first accepted reference and zeroing later references.
