# sources/test-tools/liburing/test/teardowns.c

Purpose: stress test concurrent ring setup teardown under memory pressure or allocation failure paths.

Important APIs/types/functions: `io_uring_queue_init`, fork/wait, `close`, expected `-ENOMEM`, and child exit status aggregation.

Control flow: `main()` forks 12 children. Each child runs `loop()`, attempting 100 ring initializations with depth `0xa4`; successful returns are closed immediately, and negative results other than `-ENOMEM` increment an error count. Parent waits for all children and returns the number of children reporting unexpected errors.

State/persistence behavior: state is transient kernel ring allocation/teardown state across concurrent processes. No external files or fds persist beyond each child.

Dependencies/integration: tests setup error handling and cleanup under parallelism.

Risks/test signals: detects unexpected setup errors, teardown leaks, or crashes during concurrent failed/successful ring creation. It intentionally tolerates `-ENOMEM`.
