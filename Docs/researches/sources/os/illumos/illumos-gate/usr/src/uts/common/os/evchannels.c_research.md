# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/evchannels.c

## Purpose

Implements the general-purpose sysevent event channel framework. It provides event queues, channel binding, kernel and user subscriptions, event publication, delivery threads, per-zone channel state, event snapshots, and pseudo-driver-facing userland entry points.

## Main Responsibilities

- Maintains event channels per zone through `evch_zone_key`.
- Implements basic doubly-linked lists and single queues used by channel and event queue state.
- Delivers events from channel queues to subscriber queues and then to kernel callbacks or userland doors.
- Provides kernel API wrappers `sysevent_evc_*`.
- Provides sysevent pseudo-driver support functions `evch_usr*`.
- Supports persistent subscriptions, dump subscriptions, hold-pending channels, queue limits, and channel properties.

## Key Data Structures

- `struct evch_globals`: per-zone channel list and list lock.
- `evch_chan_t`: channel descriptor with name, event queue, subscriber list, binding count, queue limits, ownership, hold-pending state, properties nvlist, publication counters, and locks.
- `evch_eventq_t`: event queue with queued events, subscriber list, delivery thread state, hold/abort flags, condition variables, current event, and traversal cursor.
- `evch_gevent_t`: refcounted event allocation wrapper with optional destructor and variable-length payload.
- `evch_subd_t`: subscription descriptor with subscriber queue, main/subscriber queue subscriptions, identity, class filter, delivery type, door/callback, persistence, dump flag, active state, and PID.
- `evch_bind_t`: per-opener binding to a channel plus list of subscriptions created through that binding.

## Event Queue Layer

- `evch_evq_create()` allocates queue state and creates the delivery thread if thread initialization has completed.
- `evch_delivery_thr()` repeatedly dequeues events, applies each subscription filter, calls delivery callbacks, handles retry/sleep results, then releases event references.
- `evch_evq_pub()` allocates a queue element, increments event refcount, queues it, and wakes the delivery thread.
- `evch_evq_stop()` and `evch_evq_continue()` hold and resume delivery, used for persistent subscribers, snapshots, and hold-pending channels.
- `evch_evq_evnext()` iterates current and queued events without allocation or locking, which is intentional for panic traversal.
- `evch_gevent_free()` decrements refcount, runs the event destructor if present, and frees the original allocation.

## Channel Layer

- `evch_chbind()` creates or finds a channel, enforces channel and binding limits, initializes hold-pending state, and returns a binding.
- `evch_chunbind()` frees a binding and destroys the channel when there are no bindings, subscribers, or retained pending events requiring indefinite hold.
- `evch_chsubscribe()` creates a per-subscriber queue, subscribes it to the channel queue with class filtering, and subscribes final delivery to either a kernel callback or userland door.
- `evch_chunsubscribe()` removes matching subscriptions, or parks persistent subscriptions by stopping their queue and dropping active door state.
- `evch_chpublish()` enforces per-channel event limits, optionally waits for space, timestamps/sequences the event, installs the destructor that decrements `ch_nevents`, and publishes to the channel queue.
- `evch_chgetnames()` and `evch_chgetchdata()` expose channel inventory and subscriber state.
- `evch_chsetpropnvl()` and `evch_chgetpropnvl()` manage a per-channel property nvlist plus generation counter.

## Delivery Paths

- Kernel delivery uses `evch_kern_deliver()` to invoke the registered callback.
- Userland delivery uses `evch_door_deliver()` with `door_ki_upcall_limited()`, exponential backoff for `EAGAIN`, sleep behavior when the process dies, and retry semantics for returned `EAGAIN`.
- Class filtering uses `evch_class_filter()` and `evch_clsmatch()`, a simple wildcard matcher with recursion bounded by `EVCH_WILDCARD_MAX`.

## Initialization and Zones

- `sysevent_evc_init()` calls `evch_chinit()`, which computes max channel/event limits from available kernel memory and creates zone-specific storage.
- `sysevent_evc_thrinit()` calls `evch_chinitthr()`, creating delivery threads for channels/subscriber queues created before thread availability.
- `evch_zonefree()` tears down all remaining channels for a zone, expecting ordinary bindings to be gone and forcibly removing persistent subscribers.

## Snapshot and Panic Traversal

- `sysevent_evc_walk_init()` snapshots subscriber and main queues into a temporary event queue during normal operation.
- During panic, it stores static traversal state and avoids allocation/locking; `sysevent_evc_walk_step()` then walks subscriber queue first, then main queue.
- `EVCH_SUB_DUMP` identifies the subscriber queue used for dump-oriented event walking; only one dump subscriber is allowed per channel.

## Kernel API Surface

- Binding/subscription/publication: `sysevent_evc_bind()`, `sysevent_evc_unbind()`, `sysevent_evc_subscribe()`, `sysevent_evc_unsubscribe()`, `sysevent_evc_publish()`.
- Control/properties: `sysevent_evc_control()`, `sysevent_evc_setpropnvl()`, `sysevent_evc_getpropnvl()`.
- Event walking: `sysevent_evc_walk_init()`, `sysevent_evc_walk_step()`, `sysevent_evc_walk_fini()`, `sysevent_evc_event_attr()`.
- Event accessors: `sysevent_get_class_name()`, `sysevent_get_subclass_name()`, `sysevent_get_seq()`, `sysevent_get_time()`, `sysevent_get_size()`, `sysevent_get_pub()`, `sysevent_get_attr_list()`.

## User/Pseudo-Driver API Surface

- `evch_usrchanopen()`, `evch_usrchanclose()`, `evch_usrallocev()`, `evch_usrfreeev()`, `evch_usrpostevent()`, `evch_usrsubscribe()`, `evch_usrunsubscribe()`, `evch_usrcontrol_set()`, `evch_usrcontrol_get()`, `evch_usrgetchnames()`, `evch_usrgetchdata()`, `evch_usrsetpropnvl()`, `evch_usrgetpropnvl()`.

## Notable Edge Cases

- Hold-pending channels can retain queued events until a subscriber appears; indefinite hold changes channel destruction behavior.
- `EVCH_QWAIT` lets publishers wait for queue capacity and return `EINTR` on signal.
- Userland channel length changes require root or channel owner.
- Door handles are released on unsubscribe or subscription failure.
