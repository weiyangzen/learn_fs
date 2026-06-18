# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmpi.h

## Role

`rsmpi.h` defines the RSM Provider Interface contract between RSM clients/kernel agent and controller drivers. It includes callback types, controller attributes, memory descriptors, scatter-gather I/O, interrupt/send-queue types, the provider operations vtable, controller acquisition APIs, and convenience dispatch macros.

## Provider Capabilities

`rsm_controller_attr_t` describes controller name/address, direct/atomic/error access sizes, error behavior, MMU protection support, page/segment/map limits, I/O-space capabilities, interrupt features, data alignment/size, piggyback support, and resource-callback support.

RSMPI interrupt service ranges divide driver, framework, reserved, Sun, and user service IDs. Send queue flags control fencing, full-queue behavior, and reliability. Send flags control queue/deliver/poll/sleep/lower-fence semantics.

## Memory and I/O

`rsm_memory_local_t` can describe local memory as virtual address, buf, export handle, or invalid. `rsmpi_iovec_t` and `rsmpi_scat_gath_t` define provider-side scatter-gather import get/put operations.

## Operations Vtable

`rsm_ops_t` includes:
- export segment create/destroy/bind/unbind/rebind/publish/unpublish/republish.
- import connect/disconnect.
- typed get/put operations for 8/16/32/64-bit values plus bulk get/put.
- import mapping/unmapping.
- barrier open/close/reopen/order and barrier-mode get/set.
- thread init/fini.
- send queue create/config/destroy/send.
- interrupt handler register/unregister.
- scatter-gather getv/putv.
- peer discovery.
- extension hook.

Macros dispatch each operation through a `rsm_controller_object_t`.

## Research Notes

This is the central RSM driver provider ABI. The vtable layout, callback sentinel values, opaque handle types, and dispatch macros must remain in sync across RSMOPS, controller drivers, and the kernel agent.
