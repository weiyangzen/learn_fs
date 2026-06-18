<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_kobject_uevent.h -->
# sources/test-tools/strace/src/netlink_kobject_uevent.h

Purpose: defines the libudev monitor header layout used by the kobject uevent decoder.

Important APIs/types/functions: `struct udev_monitor_netlink_header` with `prefix`, `magic`, `header_size`, property offsets/lengths, and filter hash/bloom fields.

Control flow: no runtime control flow.

State and persistence behavior: no state; structure definition only.

Dependencies and integration points: consumed by `netlink_kobject_uevent.c` and aligned with libudev netlink monitor payload format.

Risks: the layout is not a generic kernel `nlmsghdr`; changing it would break libudev payload rendering. Field endian expectations live in the decoder.

Test signals: compile-time structure use plus runtime uevent tests for `libudev` prefix and property payload offsets.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_kobject_uevent.h -->
