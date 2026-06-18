# sources/user-network-fs/samba/source4/lib/messaging/tests/irpc.c

`tests/irpc.c` is the local torture suite for IRPC over source4 messaging. It creates two messaging contexts on the same event loop, registers generated echo interface calls on both, and verifies synchronous, deferred, and high-volume asynchronous RPC behavior. Key test handlers are `irpc_AddOne()` and `irpc_EchoData()`, with `deferred_echodata()` proving delayed replies through `irpc_send_reply()`.

`irpc_setup()` configures a temporary pid directory, creates contexts with task IDs 1 and 2, and registers `ECHO_ADDONE` and `ECHO_ECHODATA`. `test_addone()` exercises NDR request/reply and edge input values. `test_echodata()` validates deferred payload echo. `test_speed()` sends asynchronous calls with a bounded backlog and drains replies through the shared tevent loop.

The suite does not persist data outside messaging socket/name state under the test pid directory. Risks covered include nested event loops, call-id routing, deferred reply ownership, async completion, and timeout/backlog pressure. Gaps include cross-process IRPC name lookup and security-token propagation. It is a strong regression signal for `messaging.c` IRPC binding-handle behavior.
