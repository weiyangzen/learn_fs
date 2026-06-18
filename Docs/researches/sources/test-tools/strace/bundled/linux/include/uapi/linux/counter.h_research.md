# sources/test-tools/strace/bundled/linux/include/uapi/linux/counter.h

Purpose: defines the userspace ABI for Linux Counter character devices, including component identification, event watches, event records, and related ioctl numbers.

Important APIs/types/functions: core enums are `counter_component_type`, `counter_scope`, `counter_event_type`, count direction/mode/function enums, signal level/polarity, and synapse action. `struct counter_component` identifies a device/signal/count/function/extension component; `struct counter_watch` binds a component to an event/channel; `struct counter_event` is read back with timestamp, value, watch, and status. Ioctls are `COUNTER_ADD_WATCH_IOCTL`, `COUNTER_ENABLE_EVENTS_IOCTL`, and `COUNTER_DISABLE_EVENTS_IOCTL`.

Control flow: implied userspace flow is queue one or more watches, enable event monitoring, read `counter_event` records, and disable or replace watches. The header itself only defines ioctl encoding and payload layouts.

State and persistence behavior: watch queues and enabled event sets are per character-device file instance. Events are transient runtime records with aligned 64-bit timestamp/value fields; no durable persistence is specified.

Dependencies: includes `<linux/ioctl.h>` for `_IO`/`_IOW` encoding and `<linux/types.h>` for fixed-width ABI types.

Integration points: strace decodes counter ioctl commands and can print event/watch payload structures. The ABI references sysfs component IDs documented under `Documentation/ABI/testing/sysfs-bus-counter`.

Risks: component `parent` and `id` are compact 8-bit values tied to sysfs suffixes, so tools must not assume global uniqueness. Event replacement semantics on enable are easy to miss. `status` stores system error numbers, not boolean success.

Test signals: ioctl decode tests should cover watch addition with nested component fields, enable/disable commands, and a read event with nonzero status. ABI tests should confirm ioctl numbers stay stable.
