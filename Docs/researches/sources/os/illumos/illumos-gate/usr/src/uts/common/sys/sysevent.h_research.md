# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent.h

## Purpose
Defines the public sysevent API, common event data types, limits, event-channel flags, and separate userland/kernel interfaces for publishing, subscribing, and inspecting events.

## Main Interfaces
- Opaque handles:
  - `sysevent_t`
  - `evchan_t`
- Attribute and identifier types:
  - `sysevent_attr_list_t`
  - `sysevent_attr_t`
  - `sysevent_id_t`
  - `sysevent_value_t`
  - `sysevent_bytes_t`
- Common constants:
  - event allocation flags `SE_SLEEP`, `SE_NOSLEEP`
  - sysevent error codes `SE_EINVAL` through `SE_NO_TRANSPORT`
  - publisher prefixes such as `SUNW:kern:`, `SUNW:usr:`, and `ILLUMOS:kern:`
  - class, subclass, publisher, channel, subscriber, and payload size limits
- Shared event channel APIs:
  - `sysevent_evc_bind()`, `sysevent_evc_unbind()`
  - `sysevent_evc_subscribe()`, `sysevent_evc_unsubscribe()`
  - `sysevent_evc_publish()`
  - `sysevent_evc_control()`
  - property nvlist get/set helpers
- Userland-only subscription attribute APIs and extended subscribe support.
- Kernel-only log/event construction APIs such as `log_sysevent()`, `sysevent_alloc()`, `sysevent_add_attr()`, and event getter functions.

## Dependencies And Relationships
Uses `sys/nvpair.h` and `sys/null.h`; userland path also uses `door.h`. Internal wire/storage layout and driver ioctls are defined in `sysevent_impl.h`.

## Research Notes
The publish flags distinguish allocation behavior from queue-wait behavior. `EVCH_TRYHARD` is kernel-only, while persistent subscriptions are controlled by `EVCH_SUB_KEEP`.
