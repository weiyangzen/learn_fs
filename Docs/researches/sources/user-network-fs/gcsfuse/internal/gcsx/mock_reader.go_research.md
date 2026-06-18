## sources/user-network-fs/gcsfuse/internal/gcsx/mock_reader.go

Purpose: provides a testify mock implementation of the generic `Reader` interface.

Important APIs/types/functions: `MockReader`, `ReaderName`, `ReadAt`, `Destroy`, and `CheckInvariants`.

Control flow: `ReaderName` returns the fixed string `mock_reader`. `ReadAt` delegates to testify expectations using the context and `*ReadRequest`, returning a `ReadResponse` and error. Lifecycle methods record expectation calls.

State/persistence behavior: no production state or persistence. All behavior is driven by mock expectations in tests.

Dependencies/integration: depends on `context`, `ReadRequest`, `ReadResponse`, and testify `mock`. Used by read-manager or wrapper tests needing a controllable `gcsx.Reader`.

Risks/test signals: incorrect return types in test setup panic due to type assertion. The fixed reader name is useful for assertions but may mask production-specific names in tests.
