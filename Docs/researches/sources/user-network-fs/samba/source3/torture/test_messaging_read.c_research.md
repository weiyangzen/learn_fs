# sources/user-network-fs/samba/source3/torture/test_messaging_read.c

Purpose: This file tests edge cases in `messaging_read`: competing readers for the same message type, freeing one pending request from another request's callback, repeated ping/pong against a child process, and large message payload transfer.

Important APIs/types/functions: `msg_count_send()` creates a persistent read loop that increments a counter and re-arms `messaging_read_send()`. `msg_free_send()` frees another pending request when its own read completes. `msg_pingpong_send()` sends `MSG_PING` and waits for `MSG_PONG`. `ping_responder()` runs a child event loop until an exit pipe fires. `read4_child()` and `read4_parent()` transfer a 1 MB `MSG_TORTURE_READ4` payload. Public tests are `run_messaging_read1()` through `run_messaging_read4()`.

Control flow: `run_messaging_read1()` starts two readers for `MSG_SMB_NOTIFY`, sends one message to itself, runs two event iterations, and expects only the first counter to increment. `run_messaging_read2()` starts a read whose callback frees the second pending read and verifies no second callback fires. `run_messaging_read3()` forks a responder, sends 100 ping/pong requests to the child pid, then signals exit. `run_messaging_read4()` forks a child receiver, sends a 1 MB iovec message, waits for child confirmation, and reaps it.

State/persistence behavior: All state is in process-local messaging contexts, tevent requests, pipes, child processes, and transient message buffers. No persistent files are created. The tests intentionally mutate tevent request ownership/lifetime to catch use-after-free or double-dispatch bugs.

Dependencies and integration points: It depends on Samba messaging, tevent Unix helpers, process synchronization, and the automatic MSG_PING/MSG_PONG messaging behavior. It covers infrastructure used broadly by source3 multi-process services.

Risks: Reentrant free behavior is delicate; a bug may surface as crashes rather than clean NTSTATUS failures. Large payload transfer depends on messaging fragmentation and memory availability. Child process cleanup must be reliable to avoid hanging tests.

Test signals: Expected outcomes are count `1/0` in read1, zero count after freeing the second request in read2, 100 successful ping/pong cycles in read3, and successful receive/confirmation of the 1 MB message in read4.
