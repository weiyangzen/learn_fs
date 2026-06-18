# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/636

## Purpose
This fixture validates a KMSAN uninitialized-value report in `ppp_send_frame`.

## Important APIs, types, and functions
Important frames include `ppp_send_frame`, `__ppp_xmit_process`, `ppp_xmit_process`, `ppp_write`, `do_iter_write`, `do_writev`, `__x64_sys_writev`, `__alloc_skb`, and `__kmalloc_node_track_caller`.

## Control flow
A userspace `writev` to PPP allocates an skb in `ppp_write`, then transmit processing consumes uninitialized data in `ppp_send_frame`.

## State and persistence behavior
The fixture persists KMSAN creation stack for the skb allocation and the consuming transmit stack.

## Dependencies and integration points
It tests KMSAN parsing across character-device write paths, skb allocation, and PPP network transmit logic.

## Risks and test signals
The parser must use `ppp_send_frame` as the bug site and keep the `KMSAN-UNINIT-VALUE` type.
