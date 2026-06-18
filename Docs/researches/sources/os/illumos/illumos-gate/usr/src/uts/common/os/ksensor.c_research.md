# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ksensor.c

## Purpose

`ksensor.c` implements the genunix side of the illumos kernel sensor framework. It lets kernel providers register sensor operations and metadata while a separate ksensor character driver creates/removes user-visible minor nodes under `/dev/sensors`.

Read completely: 869 lines.

## Main Responsibilities

- Maintains global sensor registration state independent of the load state of the ksensor character device.
- Tracks sensors by stable numeric IDs in an AVL tree and by owning `dev_info_t` in per-DIP lists.
- Provides `ksensor_create()` and `ksensor_remove()` for providers, including helper `ksensor_create_scalar_pcidev()` for PCI scalar sensors.
- Provides `ksensor_register()` and `ksensor_unregister()` for the ksensor character driver callback interface.
- Implements serialized sensor access through `ksensor_hold_by_id()` and `ksensor_release()`.
- Dispatches sensor operations `ksensor_op_kind()` and `ksensor_op_scalar()` after obtaining a valid provider hold.
- Handles provider detach/re-attach semantics so stale minor nodes can trigger driver reconfiguration rather than disappearing immediately.
- Cleans up permanently removed devices through DDI unbind callbacks and deferred taskq work.

## Important Data Structures And Globals

- `ksensor_t`: per-sensor object with mutex/CV, flags, waiter count, ID, name, class, provider ops, provider argument, owning `ksensor_dip_t`, list linkage, and AVL linkage.
- `ksensor_dip_t`: per-provider-DIP object containing the `dev_info_t`, DDI unbind callback, removal flag, and sensor list.
- `ksensor_g_mutex`: global lock protecting `ksensor_dips`, `ksensor_avl`, callback registration state, and ID-space use.
- `ksensor_ids`: ID allocator for sensor minor IDs.
- `ksensor_cb_dip`, `ksensor_cb_create`, `ksensor_cb_remove`: single registered character-driver callback endpoint.
- Sensor flags: `KSENSOR_F_NOTIFIED`, `KSENSOR_F_VALID`, and `KSENSOR_F_BUSY`.
- DIP flag: `KSENSOR_DIP_F_REMOVED`.

## Sensor Lifetime

The framework distinguishes provider detach from permanent device removal. `ksensor_create()` makes a sensor valid and visible; `ksensor_remove()` only clears `KSENSOR_F_VALID` and drops the provider ops/arg. The sensor object and minor-node identity remain so a later user access can attempt to reconfigure the provider's parent and revive the sensor, matching normal devfs behavior for detached devices.

Permanent removal is handled by `ksensor_dip_unbind_cb()`. The synchronous callback removes the provider from global lists, marks it removed, and removes all sensors from the ID AVL so new lookups fail. Deferred taskq cleanup then notifies the character driver to remove minors, waits for active/busy users and waiters to drain, frees each sensor, and frees the `ksensor_dip_t`.

## Access Path

`ksensor_hold_by_id()` performs the framework's open-like validation:

- Looks up the ID under the global lock.
- Rejects permanently removed provider DIPs.
- Serializes access with `KSENSOR_F_BUSY`; signalable waiters restart lookup after the busy holder exits.
- Drops framework locks before entering the devinfo tree.
- Enters the parent DIP, takes a hold on the provider DIP, and exits the parent.
- Rechecks removal and validity after the hold.
- If invalid, calls `ndi_devi_config()` on the parent to attempt reattach and then verifies that the sensor became valid.

`ksensor_release()` drops the provider DIP hold, clears busy, and wakes waiters. `ksensor_op_kind()` and `ksensor_op_scalar()` are thin wrappers that hold, invoke the provider operation vector, and release.

## Provider API

`ksensor_create()` requires a non-NULL DIP, ops, name, class, and output ID pointer, and only succeeds while the provider DIP is attaching. It creates a `ksensor_dip_t` on first use, registers a DDI unbind callback, reuses an existing invalid sensor with the same name/class, or allocates a new sensor ID. If the character driver is registered, it calls the create callback and sets `KSENSOR_F_NOTIFIED` on success.

`ksensor_remove()` requires the provider to be attaching or detaching. It finds the owning DIP and invalidates either the requested ID or all IDs (`KSENSOR_ALL_IDS`) by clearing valid state and provider callbacks.

`ksensor_create_scalar_pcidev()` validates that the provider is PCI/PCIe, reads the `reg` property, derives bus/device identifiers, picks a class from the sensor kind, and creates a name of the form `<bus>.<device>:<name>`.

## Character Driver API

Only one ksensor character driver can register. `ksensor_register()` stores its callbacks and walks all registered sensors, invoking the create callback for each and setting `KSENSOR_F_NOTIFIED` when successful. `ksensor_unregister()` validates the registering DIP, clears all notified flags, and removes callback pointers; it does not call the remove callback because the driver can remove its minors during detach.

## Locking And Concurrency

The file documents and follows these lock rules:

- `ksensor_g_mutex` protects global data and is acquired before any individual sensor mutex.
- A thread should not hold two sensor mutexes.
- No framework locks should be held while entering or manipulating devinfo tree state.
- Unless a sensor is actively held, users must recheck provider removal and sensor validity.

The busy flag serializes attach/revalidation and provider operation dispatch per sensor. Deferred unbind cleanup waits for both `KSENSOR_F_BUSY` and waiter count to drop before freeing a sensor.

## Notable Risks And Invariants

- Provider create/remove calls are constrained to attach/detach contexts; callers outside those contexts receive `EAGAIN`.
- `ksensor_hold_by_id()` intentionally drops locks around devinfo operations, so it must repeat removal/validity checks after reacquiring locks.
- `ksensor_release()` assumes a provider DIP hold was successfully obtained by the hold path.
- `ksensor_unregister()` panics if called by a DIP other than the registered character driver.
- Callback create failures leave sensors registered but not marked notified; a later character-driver register or sensor recreation can retry notification.

## Research Relevance

For storage and OS research, `ksensor.c` is not filesystem-specific, but it shows a modern illumos pattern for separating kernel provider registration from devfs-visible character devices. Its detach/reconfigure behavior, devinfo holds, unbind callbacks, and minor persistence are directly relevant to driver lifetime models used elsewhere in the device and storage stack.
