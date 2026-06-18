# sources/sync-backup/rsync/hlink.c

## Purpose

`hlink.c` implements hard-link preservation. On the sender it maps device/inode pairs into hard-link group numbers or first-link indices. On the receiver/generator it orders group members, links later members to completed leaders, handles skipped links, and remembers prior incremental-recursion hard-link paths across file lists.

## Important APIs, Types, And Functions

Under `SUPPORT_HARD_LINKS`, exported functions are `init_hard_links()`, `idev_find()`, `idev_destroy()`, `match_hard_links()`, `hard_link_check()`, `hard_link_one()`, `finish_hard_link()`, and `skip_hard_link()`.

Static state includes `data_when_new`, `dev_tbl`, `prior_hlinks`, and `hlink_flist`. `dev_tbl` is a nested 64-bit hash: device key to inode hash table. `prior_hlinks` is a 32-bit hash used by the receiver in incremental recursion to remember prior hard-link group paths or previous indices.

## Control Flow

`init_hard_links()` creates sender/old-protocol device tables or receiver incremental prior-link tables depending on role and protocol. `idev_find()` offsets device ids by one so real device zero can be represented, creates an inode table per device, and returns the inode node, using `-1` as the new-node data sentinel. `idev_destroy()` frees all nested inode tables before freeing `dev_tbl`.

`match_hard_links()` runs after a file list is sorted. It gathers sorted indices of hard-linked files and calls `match_gnums()`. `match_gnums()` sorts those indices by group number, marks first and last members, fills `F_HL_PREV()` as a reverse linked list using wire indices, and in incremental recursion updates or consults `prior_hlinks` so groups spanning file lists remain connected.

`hard_link_check()` is called by the generator for hard-linked entries that are not first. It uses `check_prior()` to find a prior unskipped group member or cached prior path. If the prior member is still being transferred, it rewires predecessor fields, marks the current file as waiting, increments `cur_flist->in_progress`, and returns skip. If a prior completed leader exists, it stats the leader, optionally considers alternate basis directories, then calls `maybe_hard_link()` to create or verify the hard link.

`finish_hard_link()` is called when a leader transfer or local match is complete. It marks the leader done, stores `alt_dest` in `F_HL_PREV()` for first/done entries, walks the waiting reverse chain, calls `maybe_hard_link()` for each follower, decrements `in_progress`, sends remove-source success messages when needed, and in incremental recursion replaces the prior hash data with a cached pathname. `skip_hard_link()` marks skipped entries and promotes a previous waiting member to last when necessary.

## State And Persistence

Hard-link state is stored in file-list extra fields and in process-local hash tables. For protocol 30 and later, the sender transmits a first hard-link index instead of raw dev/inode for every member. For older protocols the receiver groups dev/inode itself. Incremental recursion persists group continuity in `prior_hlinks` while the process runs; it is not written to disk.

## Dependencies And Integration Points

This file depends on `hashtable.c`, `flist.c` lookup/index functions, `generator.c` APIs (`itemize()`, `quick_check_ok()`, `unchanged_attrs()`, `atomic_create()`), filesystem wrappers (`link_stat()`, `do_link_at()`), alternate basis directories, ACL/xattr accessors, and message/logging helpers. It is tightly coupled to `file_struct` hard-link macros from rsync headers.

## Risks

The code relies on overloading `F_HL_PREV()` for previous indices, first/done alternate-destination ids, and waiting-chain links. Incorrect flag combinations can create cycles, strand `in_progress`, or link to the wrong file. Incremental recursion has extra risk because prior groups may be skipped, freed, or represented only by cached path strings. Dry-run and alt-dest behavior can report a link target that is not actually present. Platform limits around hard-linking symlinks, devices, and special files are conditional and must match compile-time capabilities.

## Test Signals

Tests should cover hard-linked regular files in sorted and unsorted index modes, protocol pre-30 and post-30, incremental recursion groups spanning multiple file lists, skipped first/last/middle members, leaders still transferring, dry-run with link-dest, remove-source-files success, hard-linking symlinks/specials where supported and unsupported, alt-dest matches, and error paths for missing prior leaders.
