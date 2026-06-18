# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hidvar.h

Internal HID driver state header. It defines boot-interface/protocol constants, fallback keyboard/mouse packet and report descriptor sizes, HID control request values, mctl return codes, stream-open flags, timeout/retry constants, and debug masks.

The central structures are `hid_power_t`, which tracks PM strategy, wakeup, busy accounting, supported/current power states, and pending power-up message state, and `hid_state_t`, which owns per-instance USBA registration, descriptors, default/interrupt pipe handles, parser handle, packet sizing, polled console state, STREAMS queues, logging, and ugen support.

Concurrency is documented with Warlock `_NOTE` annotations: `hid_mutex` protects `hid_state_t` and `hid_power_t`, while several handles/descriptors are declared stable/readable without the lock. The file also records the driver's online/suspended/disconnected/powered-down/power-change state model.

Notable detail: there is a `_NOTE(DATA_READABLE_WITHOUT_LOCK(hid_state_t::hid_ep_intr_descr))` reference, while the actual struct field is `hid_ep_intr_xdescr`; this may be a stale annotation name.
