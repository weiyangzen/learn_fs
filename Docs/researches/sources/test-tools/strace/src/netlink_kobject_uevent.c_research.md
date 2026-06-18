<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_kobject_uevent.c -->
# sources/test-tools/strace/src/netlink_kobject_uevent.c

Purpose: decodes `NETLINK_KOBJECT_UEVENT` payloads, especially libudev monitor headers followed by property strings.

Important APIs/types/functions: `decode_netlink_kobject_uevent`, `PRINT_FIELD_HTONL_X`, and `struct udev_monitor_netlink_header`.

Control flow: if verbose mode, successful syscall state, valid address/length, and `"libudev"` prefix all match, it prints the libudev header fields and trailing property string data. Otherwise it prints the payload as a string buffer.

State and persistence behavior: no persistent state; it decodes one payload buffer.

Dependencies and integration points: called directly from `decode_netlink` when the fd family is `NETLINK_KOBJECT_UEVENT`; depends on `netlink_kobject_uevent.h`, tracee memory fetch, and network byte-order formatting.

Risks: non-libudev kernel uevents are intentionally string-only. Header validation is prefix based; malformed or short libudev-like payloads fall back rather than partially decoding.

Test signals: cover raw kernel uevent strings, valid libudev headers with properties, short buffers, failed syscalls, nonverbose mode, and big-endian formatted filter hashes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_kobject_uevent.c -->
