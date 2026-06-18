# sources/test-tools/strace/tests/netlink_kobject_uevent.c

Purpose: tests decoding of `NETLINK_KOBJECT_UEVENT` payloads, including libudev-style monitor frames, kernel uevent strings, concatenated records, and malformed/truncated data.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_KOBJECT_UEVENT)`, `sendto`, `sprintrc`, `struct udev_monitor_netlink_header` from `netlink_kobject_uevent.h`, `htonl`, `print_quoted_string`, and buffer-filling helpers.

Control flow: helper `send_uevent` sends arbitrary buffers and captures the result. Test functions print expected decoding for monitor headers with magic/properties, arrays of environment strings, plain quoted strings, empty input, and raw hexadecimal fallback.

State and persistence: all data is synthetic user-space buffers sent to a transient netlink socket. No udev or kernel device state is changed.

Dependencies and integration points: uses the strace kobject uevent decoder and local header definitions for monitor metadata. It exercises both structured and unstructured payload branches.

Risks and edge cases: NUL-separated string parsing, network-endian header fields, short buffers, embedded empty strings, and fallback from structured to raw printing are primary risks.

Test signals: expected output should show `sendto` payloads as decoded uevent objects where possible and quoted/raw bytes otherwise, with stable syscall return formatting.
