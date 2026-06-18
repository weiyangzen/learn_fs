# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/vendor.c

`vendor.c` handles OpenBSD vendor ID payload support for `isakmpd`. It hashes configured vendor capability strings with MD5 at startup and can add/check corresponding ISAKMP Vendor ID payloads.

The current table contains `OpenBSD-6.3`. `vendor_init()` prepares hashes, `add_vendor_openbsd()` appends vendor payloads to outgoing messages, and `check_vendor_openbsd()` compares inbound payloads and sets `EXCHANGE_FLAG_OPENBSD` on a match.

This is compatibility/capability signaling rather than authentication. Payloads are marked as processed whether already known or matched during the check.
