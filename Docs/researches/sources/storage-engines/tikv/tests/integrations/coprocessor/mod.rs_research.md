# sources/storage-engines/tikv/tests/integrations/coprocessor/mod.rs

## sources/storage-engines/tikv/tests/integrations/coprocessor/mod.rs

Purpose: module aggregator for coprocessor integration tests.

Important APIs/types/functions: declares `test_analyze`, `test_checksum`, and `test_select`; no runtime code.

Control flow/state: Rust test discovery runs the child modules through this file. Persistence and state are in child test fixtures.

Dependencies and integration points: parent integration test crate and `test_coprocessor` helpers used by children. Risk is accidentally dropping a module declaration and losing test coverage. Test signal is compilation and execution of the listed child modules.
