# File Research: sources/local-fs/xfsprogs/repair/phase7.c

## Role

`phase7.c` implements the final link-count verification and correction phase. It compares each live inode’s disk link count against the reference count accumulated during directory traversal and fixes mismatches when not in no-modify mode.

## Core Flow

- `phase7()` sets the progress message, initializes quotacheck, creates a workqueue, and queues one link-count update task per AG.
- `do_link_updates()` walks all confirmed non-free inodes in an AG, compares recorded disk nlinks to counted references, updates mismatches, and feeds each inode to `quotacheck_adjust()`.
- `update_inode_nlinks()` opens the inode in a transaction and logs the core after calling `set_nlink()`.
- After all AGs complete, phase 7 verifies user, group, and project quota counters and tears down quotacheck state.

## Dependencies

It depends on the in-core inode tree populated by earlier phases, libxfs inode/transaction APIs, workqueues, progress reporting, and `quotacheck.c`.

## Risk Areas

- In write mode, assertions assume all non-free inodes were reached and have positive reference counts.
- If phase 6 reachability/reference accounting is wrong, phase 7 will make link counts match that wrong model.
- Quotacheck is coupled to this phase because it piggybacks on the final live-inode scan.
