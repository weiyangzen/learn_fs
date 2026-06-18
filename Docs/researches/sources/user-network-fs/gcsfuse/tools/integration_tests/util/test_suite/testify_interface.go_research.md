# sources/user-network-fs/gcsfuse/tools/integration_tests/util/test_suite/testify_interface.go

Purpose: small interface adapter for testify suite types.

Important APIs/types/functions: `TestifySuite`, embedding `suite.TestingSuite` and requiring `Run(name string, subtest func()) bool`.

Control flow: no executable flow; it allows helpers to accept suite values that can run subtests.

State/persistence behavior: no state or persistence.

Dependencies/integration: depends on `github.com/stretchr/testify/suite`.

Risks/test signals: interface is narrow and useful for compile-time abstraction; no direct tests are present in this file.
