# File Research: sources/virtualization/spdk/lib/nvme/nvme_poll_group.c

## Purpose

Implements the public NVMe poll-group abstraction over transport-specific poll groups. It groups qpairs by transport, optionally integrates interrupt/eventfd handling, validates accelerator callback tables, dispatches completion polling/waiting, and aggregates per-transport stats.

## Main Responsibilities

- Create/destroy `spdk_nvme_poll_group`, initialize optional accel function table, fd group, disconnect eventfd, context, and transport-group list.
- Validate that acceleration sequence callbacks are all present or all absent, and that append callbacks have required sequence callbacks.
- Add/remove qpairs by finding or creating the matching transport poll group.
- Enforce that all qpairs in one poll group use the same interrupt mode.
- In Linux interrupt mode, create a disconnect eventfd, add qpair fds to the fd group, and invoke the configured interrupt callback when events arrive.
- Connect/disconnect qpairs through transport callbacks while adding/removing qpair fd handlers.
- Process completions across transport groups with recursion protection.
- Wait for fd-group events after checking disconnected qpairs.
- Report whether all qpairs are connected, preserving disconnected qpair priority over still-connecting state.
- Aggregate and free per-transport poll-group statistics.

## Key Control Flow

`spdk_nvme_poll_group_add()` requires qpairs to be disconnected, initializes interrupt-mode consistency on first add, lazily creates a transport-specific poll group, and delegates add to the transport. `spdk_nvme_poll_group_process_completions()` iterates all transport groups and returns the first negative transport error if any, otherwise total completions.

## Integration Points

Calls transport abstraction functions from `nvme_internal.h`, qpair state helpers, fd group APIs, Linux `eventfd`, and the PCIe/fabrics transport poll-group implementations.

## Risk Notes

- Destroy returns `-EBUSY` if any transport poll group cannot be destroyed, preserving the group list for retry.
- Interrupt fd handling has Linux-specific behavior; non-Linux builds stub disconnect fd support with `-ENOTSUP`.
- `spdk_nvme_poll_group_wait()` assumes fd group support exists and a non-null disconnected-qpair callback is supplied.
