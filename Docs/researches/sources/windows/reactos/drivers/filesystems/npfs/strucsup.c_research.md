# File Research: sources/windows/reactos/drivers/filesystems/npfs/strucsup.c

## Purpose
Allocates, initializes, and deletes NPFS core structures: VCB, root DCB, FCBs, CCBs, root DCB CCBs, and event-table entries.

## Main Responsibilities
- Globals:
  - `NpRootDCBName`
  - `NpVcb`
- Event-table callbacks:
  - `NpEventTableCompareRoutine`
  - `NpEventTableAllocate`
  - `NpEventTableDeallocate`
  - These are unimplemented.
- `NpDeleteEventTableEntry` dereferences an event and deletes the table element.
- `NpInitializeVcb` zeroes VCB, initializes prefix table, resource, generic event table, and wait queue.
- `NpCreateRootDcb` allocates root DCB, initializes lists/name fields, and inserts `\` into the prefix table.
- `NpCreateRootDcbCcb` allocates a root directory handle context.
- `NpCreateFcb` allocates a pipe FCB:
  - Normalizes names to leading backslash.
  - Allocates full-name buffer.
  - Inserts into parent DCB list and prefix table.
  - Stores pipe instance/type/configuration metadata.
- `NpCreateCcb` allocates paged and nonpaged CCB portions:
  - Initializes inbound/outbound queues.
  - Inserts into FCB CCB list.
  - Increments current instance and server-open counts.
- `NpDeleteCcb` tears down CCB resources and queues.
- `NpDeleteFcb` cancels waiters, removes prefix/list links, releases security descriptor, and frees name/FCB memory.

## Important Interactions
- Core allocation layer for `create.c`.
- Deletion is driven by `statesup.c` and close/cleanup paths.
- Prefix table entries are consumed by `prefxsup.c`.

## Risks / Review Notes
- Event table is not usable because compare/allocate/deallocate callbacks are stubs.
- `NpDeleteCcb` decrements `CurrentInstances` but not `ServerOpenCount`; server-open accounting depends on other cleanup/close code outside this file.
- FCB deletion bugchecks if current instances remain, enforcing lifecycle ordering.
