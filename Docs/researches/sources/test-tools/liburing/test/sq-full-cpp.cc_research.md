# sources/test-tools/liburing/test/sq-full-cpp.cc

Purpose: C++ compilation variant of the SQ-full test, confirming liburing headers and `io_uring_get_sqe()` behavior work under C++.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_get_sqe`, `io_uring_queue_exit`, and queue depth 8.

Control flow: initializes an 8-entry ring, repeatedly calls `io_uring_get_sqe()` until it returns NULL, and expects exactly 8 SQEs.

State/persistence behavior: only ring SQ state is used. No external state or persistence.

Dependencies/integration: exercises the C++ build/link path for liburing test code and the same runtime helper behavior as the C version.

Risks/test signals: catches header incompatibility in C++ builds or incorrect SQE accounting when the submission queue fills.
