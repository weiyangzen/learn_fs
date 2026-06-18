# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ioctl.h

## Purpose
Defines the user/kernel HAMMER ioctl ABI, including command numbers, shared request structures, mirror stream record formats, and operation flags.

## Key Elements
- Common `hammer_ioc_head` carries flags, error, and reserved ABI space.
- Defines prune, rebalance, history, reblock, synctid, info, PFS, mirror, version, volume, snapshot, config, dedup, and get-data request structures.
- Documents iteration fields such as `key_beg`, `key_end`, `key_cur`, `nxt_tid`, `nxt_key`, `index`, and `count`.
- Defines mirror stream records: generic header, record payload, skip range, update, sync, PFS data, and union wrapper.
- Defines mirror record types and CRC/error/no-data flags, including byte-order signature constants.
- Provides ioctl command IDs `HAMMERIOC_PRUNE` through `HAMMERIOC_SCAN_PSEUDOFS`.

## Dependencies
Includes `<sys/param.h>`, `<sys/ioccom.h>`, and `hammer_disk.h`, making it usable from userland as well as kernel code.

## Behavior/Risks
This is a stable ABI surface. Structure sizes, reserved fields, aligned mirror records, and flag meanings are part of userland compatibility. The header explicitly notes that config records are not mirrored and that snapshot get results may require caller-side sorting due to signed B-tree key ordering.
