# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/device_impl.h

`device_impl.h` defines kernel-private device contract structures. Device templates store common template data, accepted event set, nonegotiable flags, minor path, and acknowledgement time. Device contracts store common contract data, devinfo pointer, dev_t, spec type, device state, event set, nonegotiable flags, vnode data, minor path, and ack time.

It declares device contract type state and lifecycle/event functions for init, offline negotiation, degrade/undegrade, open, and removing contracts tied to a devinfo node.
