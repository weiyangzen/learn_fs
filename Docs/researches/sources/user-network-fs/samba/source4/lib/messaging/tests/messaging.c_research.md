# sources/user-network-fs/samba/source4/lib/messaging/tests/messaging.c

`tests/messaging.c` is the local torture suite for raw imessaging datagrams. It defines ping/pong/exit callbacks, overflow tests, checksum validation across a forked child, and multi-context delivery tests. `torture_local_messaging()` registers `overflow`, `overflow_check`, `ping_speed`, and `multi_ctx`.

`test_ping_speed()` creates client/server contexts, registers temporary message handlers, sends payload and NULL-payload pings for a configurable timelimit, and drains replies. `test_messaging_overflow()` sends many pings to a forked child to ensure queue pressure does not break initialization or cleanup. `test_messaging_overflow_check()` streams random payloads to a child and compares MD5 digests returned over messaging. `test_multi_ctx()` sends to `cluster_id(0,0)` and frees contexts from inside callbacks, proving dispatch iteration survives callback-side destruction.

State is limited to temporary pid/socket directories and process memory. Dependencies include tevent, cluster IDs, GnuTLS hashing, fork/pipe synchronization, and loadparm. Risks tested include fd rejection, queue overflow, message loss, broadcast semantics, and use-after-free during callback dispatch. Gaps include privilege retry and non-local cluster behavior.
