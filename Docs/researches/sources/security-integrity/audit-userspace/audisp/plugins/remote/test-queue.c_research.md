# sources/security-integrity/audit-userspace/audisp/plugins/remote/test-queue.c

Purpose: exercises the persistent queue implementation used by audisp-remote.

Important APIs and data: uses `q_open`, `q_append`, `q_peek`, `q_drop_head`, `q_queue_length`, and `q_close` with `NUM_ENTRIES = 7` and `ENTRY_SIZE = 12288`. Generates random NUL-terminated sample entries.

Control flow: tests open flags and locking, empty queue behavior, basic append/peek/drop, maximum entry size rejection, wraparound, reopen persistence for file queues, memory-only non-persistence, and queue resizing up/down constraints.

State and persistence: creates a temporary `/tmp/tqXXXXXX` file and removes it after each file-backed test.

Dependencies and integration: wired into `make check` by remote `Makefile.am`.

Risks: uses random sample contents but not a fixed seed, though comparisons are self-contained. It does not simulate corrupt persistent files or crash windows.

Test signals: this file is the direct automated test signal for `queue.c`; failures abort with line-numbered messages.
