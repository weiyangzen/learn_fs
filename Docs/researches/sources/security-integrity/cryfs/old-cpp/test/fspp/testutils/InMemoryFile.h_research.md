# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/InMemoryFile.h

Purpose: declares immutable and writable in-memory file helpers for CryFS tests.

Important APIs/types: `InMemoryFile` owns protected `cpputils::Data _data` and exposes `read`, `data`, `size`, and `fileContentEquals`. `WriteableInMemoryFile` adds `write`, `sizeUnchanged`, and `regionUnchanged`, plus private extension helpers and `_originalData`.

Control flow/state: construction moves in a `Data` buffer; the writable subclass uses inheritance to mutate `_data` and keeps an original copy for assertions.

Dependencies/integration: includes cpp-utils `Data` and fspp byte-count types. It is designed to plug into mock read/write tests.

Risks: raw `const void*` exposure lets callers compare or copy data but not safely know lifetime beyond the object. The class is not synchronized.

Test signals: expected to be used in unit tests for file operation semantics; no direct tests in this header.
