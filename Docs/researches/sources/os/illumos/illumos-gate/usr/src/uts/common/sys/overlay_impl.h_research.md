# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_impl.h

## Purpose

`overlay_impl.h` defines the internal kernel structures and subsystem interfaces for illumos overlay devices. It connects overlay plugins, socket multiplexers, target resolution, MAC device state, fault-management status, property handling, and transmit/receive coordination.

## Core Structures

`overlay_plugin_t` stores registered encapsulation plugin metadata, ops, properties, ID size, flags, destination requirements, active count, and list linkage. Mutable fields are protected by `ovp_mutex` or global plugin locking as commented.

`overlay_mux_t` represents a shared socket/mux instance for a plugin and socket tuple. It owns the kernel socket, protocol/address metadata, active instance count, and an AVL tree of devices.

`overlay_target_t` stores point or dynamic target-resolution state, with teardown flag, open count, condition variable, destination mode/type/ID, and either a point target or dynamic refhash/AVL state.

`overlay_dev_t` is the central per-overlay device object. It tracks MAC handle, plugin, datalink ID, plugin private pointer, refcount, MTU, flags, RX/TX counts, mux pointer, virtual network ID, mux AVL node, target pointer, and fault-management message. Flags distinguish activation, mux membership, active TX/RX, metadata-drop, stopping, varpd existence, degraded state, and mask values.

`overlay_target_entry_t` tracks dynamic destination entries: locks, refhash/AVL/list linkage, pending/valid/drop flags, MAC address, target/device pointers, destination socket address, queued blocked mblks, outstanding size, and valid timestamp.

## Internal Interfaces

The header declares the overlay control name, a DTrace-backed `OVERLAY_FREEMSG()` macro, global `overlay_dip`, MAC transmit entry point `overlay_m_tx()`, device iteration, plugin lookup/release/walk lifecycle, I/O start/done accounting, mux lifecycle/open/close/add/remove/transmit, property initialization, target open/ioctl/close/free/lookup/quiesce lifecycle, fault-management degrade/restore, and datalink-ID hold/release helpers.

Target lookup returns `OVERLAY_TARGET_OK`, `OVERLAY_TARGET_DROP`, or `OVERLAY_TARGET_ASYNC`.

## Research Notes

This header encodes the overlay subsystem's locking and lifetime model. Audit-sensitive areas include device refcount and stop-mask transitions, TX/RX active counters, mux device AVL membership, plugin active counts, target-entry pending queues, async lookup completion, and degradation metadata updates while traffic is being dropped.
