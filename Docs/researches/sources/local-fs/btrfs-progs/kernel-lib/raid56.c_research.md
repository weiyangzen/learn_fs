# File Research: sources/local-fs/btrfs-progs/kernel-lib/raid56.c

## Purpose
Portable userspace RAID5/RAID6 parity generation and recovery helpers for btrfs-progs.

## Key Interfaces
- `raid6_gen_syndrome(disks, bytes, ptrs)` generates P and Q syndrome blocks.
- `raid5_gen_result(nr_devs, stripe_len, dest, data)` regenerates a RAID5 missing stripe by XOR.
- `raid6_recov_data2(...)` recovers two missing RAID6 data stripes.
- `raid6_recov_datap(...)` recovers one data stripe plus P parity.
- `raid56_recov(...)` dispatches RAID5/RAID6 recovery based on btrfs profile and missing stripe indexes.

## Dependencies
Includes volume/profile definitions, btrfs tree constants, RAID table declarations from `raid56.h`, and message helpers.

## Notable Behaviors
- Uses native-word unaligned loads/stores for portable syndrome generation.
- RAID5 with two devices is treated as RAID1 and copied from the mirror.
- `raid56_recov()` normalizes `dest1`/`dest2`, rejects unrecoverable RAID5 dual failures, regenerates P/Q directly when only parity is missing, and handles data+Q by data recovery followed by full syndrome regeneration.

## Risks And Review Notes
- `raid6_recov_datap()` allocates `zero_mem` but does not free it before returning, causing a leak per call.
- `raid6_recov_datap()` lacks the argument validation present in `raid6_recov_data2()`; wrapper paths constrain callers, but direct callers could pass invalid indexes.
- `raid5_gen_result()` requires `stripe_len == BTRFS_STRIPE_LEN`; this rejects other lengths even though the parameter type is general.
