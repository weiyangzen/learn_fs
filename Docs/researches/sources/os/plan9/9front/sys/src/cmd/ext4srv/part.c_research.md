# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/part.c

## Purpose
Adapts a Plan 9 block device or file into an lwext4 block device and manages mounted ext4 partitions.

## Key Elements
Implements block callbacks `bdopen`, `bdread`, `bdwrite`, and `bdclose`; probes device block size from the sibling `ctl` file; mounts, recovers, starts journaling, enables write-back caching, and loads group data from either options or `/etc/group` inside the ext4 filesystem. `openpart` deduplicates by `qid.path`, optionally formats the device with `ext4_mkfs`, and links the `Part` into a global list guarded by `QLock`.

## Dependencies
Uses Plan 9 `pread`, `pwrite`, `Dir`, `Qid`, `QLock`, and random generation, plus lwext4 APIs such as `ext4_mount`, `ext4_recover`, `ext4_journal_start`, `ext4_cache_flush`, and `ext4_mkfs`.

## Behavior/Risks
Read/write callbacks require full physical-block transfers. Error paths wrap `%r` messages but some cleanup relies on partially initialized `Part` state. `_closepart` appears suspicious because the previous-link update assigns `p->prev = p->next` instead of updating the previous node's `next` field, which can leave the global part list inconsistent.
