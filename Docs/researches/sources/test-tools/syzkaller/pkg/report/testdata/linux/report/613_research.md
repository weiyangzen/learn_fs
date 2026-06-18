# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/613

## Purpose
This fixture covers a warning in `netlbl_cipsov4_add` that panics because `panic_on_warn` is enabled.

## Important APIs, types, and functions
Relevant symbols include `__alloc_pages`, `alloc_pages`, `kmalloc_order_trace`, `netlbl_cipsov4_add`, `genl_family_rcv_msg_doit`, `genl_rcv_msg`, `netlink_rcv_skb`, `netlink_sendmsg`, `__sys_sendmsg`, `panic`, and `__warn`.

## Control flow
Generic netlink receives a message, enters the NetLabel CIPSOv4 add path, attempts a high-order allocation, warns in page allocation, and then panics.

## State and persistence behavior
The top-level `PANICKED: Y` is persisted as expected parser state. Runtime state in the log is allocation parameters and syscall register state only.

## Dependencies and integration points
The fixture connects generic netlink parsing, network-label subsystem frames, allocator warning formats, and panic-on-warn suffix handling.

## Risks and test signals
The parser must keep the title as `WARNING in netlbl_cipsov4_add` rather than `__alloc_pages`, while also retaining `TYPE: WARNING` and `PANICKED: Y`.
