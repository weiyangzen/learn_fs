# sources/storage-engines/tikv/tests/integrations/config/dynamic/mod.rs

## sources/storage-engines/tikv/tests/integrations/config/dynamic/mod.rs

Purpose: module aggregator for dynamic online-config integration tests.

Important APIs/types/functions: no functions are defined; it declares child modules `gc_worker`, `pessimistic_txn`, `raftstore`, `snap`, and `split_check`.

Control flow: Rust test discovery compiles and runs the child modules through this integration module. State and persistence are delegated to children.

Dependencies and integration points: the file wires the dynamic config suite into `tests/integrations/config/mod.rs`. The risk is simple omission: a child module removed here silently drops its tests from the integration target. Test signal is successful compilation and execution of all listed child modules.
