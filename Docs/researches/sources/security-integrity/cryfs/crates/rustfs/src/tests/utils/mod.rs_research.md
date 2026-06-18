# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mod.rs

Purpose: module aggregator for rustfs test utilities. It keeps internal utility modules private and re-exports the public helpers used by the test suite.

Important APIs/types/functions: re-exports `FilesystemDriver`, `MockAsyncFilesystemLL`, `make_mock_filesystem`, `Runner`, `MockHelper`, `ROOT_INO`, and `assert_request_info_is_correct`.

Control flow: no runtime logic; compilation wires module boundaries. Tests import through this module instead of individual files.

State/persistence: none.

Dependencies/integration: integrates filesystem driver, mock low-level API, fuser runner, mock helper, and request-info assertion utilities. This is the stable facade for test code.

Risks: re-export omissions break downstream tests even when implementation modules compile. The private module list also means adding a helper requires an explicit re-export decision.

Test signals: compile failures reveal missing modules/re-exports; downstream tests exercise the exported utilities.
