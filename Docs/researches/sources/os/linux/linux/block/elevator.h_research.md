# File Research: sources/os/linux/linux/block/elevator.h

Defines the public internal interface between the block elevator core and blk-mq I/O scheduler implementations.

Key declarations:
- `enum elv_merge` defines no/front/back/discard merge outcomes.
- `struct elevator_tags` and `struct elevator_resources` carry allocated scheduler tag state and private scheduler data.
- `struct elv_change_ctx` carries state through scheduler changes, including old/new queues and allocated resources.
- `struct elevator_mq_ops` is the scheduler callback table for init/exit, hctx setup, merge, insertion, dispatch, completion, depth limiting, and ICQ lifecycle hooks.
- `struct elevator_type` describes a scheduler implementation, its sysfs/debugfs attributes, module owner, alias, and optional ICQ cache.
- `struct elevator_queue` is the per-request-queue scheduler instance, with private data, kobject, sysfs lock, flags, and merge hash.

Notable constants:
- `ELV_NAME_MAX` limits scheduler names.
- `ELV_HASH_BITS` sizes the merge hash.
- `ELEVATOR_INSERT_*` defines scheduler insertion modes used by blk-mq paths.
- `ELEVATOR_FLAG_REGISTERED` and `ELEVATOR_FLAG_DYING` gate exported lifecycle state.

Research relevance:
- This header is the contract used by `elevator.c`, `mq-deadline.c`, `kyber-iosched.c`, and blk-mq scheduler glue.
- The callback table shows which scheduler operations are mandatory versus optional.
