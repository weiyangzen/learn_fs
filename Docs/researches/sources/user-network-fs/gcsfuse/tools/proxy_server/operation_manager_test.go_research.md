# sources/user-network-fs/gcsfuse/tools/proxy_server/operation_manager_test.go

Purpose: unit tests for retry configuration grouping and retrieval semantics.

Important APIs/types/functions: `TestNewOperationManager`, `TestRetrieveOperation`, and `TestAddRetryConfig`.

Control flow: tests initialize configs with different methods, skip counts, retry counts, and repeated methods, then assert returned instruction sequences and internal map shape.

State/persistence behavior: pure in-memory tests, aside from package debug flag reads in constructors.

Dependencies/integration: uses `testify/assert`.

Risks/test signals: tests cover sequential retrieval but not concurrent access. They validate the intended stateful consumption behavior used by the proxy.
