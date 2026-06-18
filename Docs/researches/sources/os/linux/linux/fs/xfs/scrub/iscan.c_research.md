# File Research: sources/os/linux/linux/fs/xfs/scrub/iscan.c

Implements live filesystem inode scanning for scrub/repair code that must visit all allocated inodes while racing safely with inode creation, deletion, and metadata updates.

Main mechanisms:
- The scan starts at a rotating AG-derived inode number to distribute load.
- `xchk_iscan_find_next` walks the inobt under AGI lock to find the next allocated inode, optionally masking `skip_ino`.
- `xchk_iscan_move_cursor` advances both the next-scan cursor and visited cursor over sparse inode-number gaps while AGI prevents allocation/free races.
- `xchk_iscan_advance` moves across AGs until it finds allocated inodes or wraps to the start.
- `xchk_iscan_iget` grabs up to one inode chunk of consecutive allocated inodes, using noretry/dontcache flags, retrying around inodegc races, and recording skipped unallocated inodes in a mask.
- `xchk_iscan_iter_batch` and `xchk_iscan_iter` expose one inode at a time to callers while internally batching igets.
- `xchk_iscan_iter_finish`, `xchk_iscan_finish`, `xchk_iscan_finish_early`, and `xchk_iscan_teardown` release cached inodes and mark scan completion.
- `xchk_iscan_mark_visited` advances the visited cursor after the caller has safely scanned an inode.
- `xchk_iscan_want_live_update` tells hook code whether an inode has already been scanned, was skipped in a batch, or falls in the wrapped visited range, and therefore needs live update replay.

Important correctness model:
- Advancing the cursor happens while AGI is locked so inode allocation/free cannot invalidate the observed range.
- Callers must hold sufficient inode locks before marking visited.
- Live-update hook code uses the visited cursor to update scan-derived indexes for inodes modified after being scanned.
- Trylock-AGI mode supports callers that already hold locks where blocking on AGI could deadlock.
