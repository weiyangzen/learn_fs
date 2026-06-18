# sources/security-integrity/audit-userspace/audisp/test/test-queue.c

Purpose: Unit and stress-style coverage for `audisp/queue.c`, including FIFO order, persistence, wrapped resize, producer/resizer handshakes, and timed dequeue behavior.

Important APIs, types, and functions: Stubs required globals `disp_hup` and `dropped`. Uses `make_event()` to allocate `event_t` objects. Test functions are `basic_test()`, `concurrency_test()`, `persist_test()`, `resize_wrap_test()`, and `resize_handshake_test()`. Producer/consumer thread helpers generate deterministic event strings and verify order.

Control flow: `basic_test()` loads fixture log lines, enqueues them into a 16-slot queue, dequeues them, and compares data. `persist_test()` creates a temp file, initializes `Q_IN_FILE | Q_CREAT | Q_SYNC`, enqueues one event, destroys the queue, and asserts the persisted file size. `resize_wrap_test()` fills a 100-slot ring, drains 80 entries, enqueues 20 more to wrap, grows to 200, and verifies FIFO sequence from 80 through 119. `resize_handshake_test()` runs a producer and dispatcher consumer concurrently; the consumer grows the queue after 128 events and verifies all 2000 ordered logical events arrive. `concurrency_test()` runs one producer and timed dequeue loop until target minus drops is consumed.

State and persistence: Queue state is global inside `queue.c`; each test initializes and destroys it. Persistence uses `/tmp/audisp_qXXXXXX` and unlinks it at the end. The global `dropped` counter is incremented by producer paths that observe enqueue failure.

Dependencies and integration points: Links `libqueue.la` and `libaucommon.la`; uses `../../auparse/test/test3.log` as event data fixture via `srcdir`. Depends on pthreads and queue public APIs.

Risks and edge cases: The `concurrency_test()` has a second producer commented out, reflecting that the queue is documented as single producer. Timed dequeue uses an absolute-looking `timespec` with small values; because `sem_timedwait()` expects an absolute timeout on POSIX, behavior can be platform-sensitive if the call is reached when empty. The tests do not validate all overflow actions such as halt or single-user mode, which would be unsafe in unit tests.

Test signals: This is the direct regression signal for the queue's 2025 race-free resize work, FIFO preservation across wrapped rings, persistence writes, and depth accounting.
