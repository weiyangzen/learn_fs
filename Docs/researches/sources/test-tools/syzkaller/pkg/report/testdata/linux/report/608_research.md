# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/608

## Purpose
This fixture validates recognition of an `ATOMIC_SLEEP` report titled `BUG: sleeping function called from invalid context in __alloc_skb`. It models a netlink/nfnetlink send path that reaches `netlink_ack`, `__alloc_skb`, and `kmem_cache_alloc_node` while RCU/preemption context is still relevant.

## Important APIs, types, and functions
Key symbols are `___might_sleep`, `__alloc_skb`, `netlink_ack`, `netlink_rcv_skb`, `nfnetlink_rcv`, `netlink_unicast`, `netlink_sendmsg`, `__sys_sendmsg`, and `do_syscall_64`. The header fields `TITLE` and `TYPE` are the expected parser outputs.

## Control flow
The log starts with the metadata oracle, then a kernel diagnostic, lock context, preemption-disabled site in `__dev_queue_xmit`, and the syscall stack from `sendmsg`.

## State and persistence behavior
The file is static test data. It persists only the expected classification and the raw console lines needed to reproduce parser matching.

## Dependencies and integration points
It integrates with syzkaller's Linux report extraction tests and exercises parsing of sleeping-in-atomic reports that include lock-held and preemption context.

## Risks and test signals
The main risk is misattributing the title to allocation helpers instead of preserving the canonical `__alloc_skb` frame. Test success is signaled by `TYPE: ATOMIC_SLEEP` and the exact title.
