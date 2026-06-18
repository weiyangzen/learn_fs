# sources/security-integrity/cryfs/crates/rustfs/src/high_level_api/mod.rs

Purpose: module facade for the high-level path API.

Important APIs: declares `interface` and re-exports `AsyncFilesystem`, `AttrResponse`, `CreateResponse`, `OpenResponse`, and `OpendirResponse`.

Control flow and state: no runtime behavior.

Dependencies and integration: used by `lib.rs`, `object_based_api/high_level_adapter.rs`, and backend glue.

State and persistence behavior: this module does not own data, but it defines which path-oriented operation results are available to downstream filesystem implementations and backend adapters. The response types carry TTLs, attributes, and handles that control cache and persistence behavior at the FUSE boundary.

Risks and tests: public API stability depends on the re-export list matching intended surface. If a response type or trait method is added in `interface.rs` but not re-exported here, users may have to reach through private module paths or lose access entirely. Coverage is indirect through adapters and mounted tests.
