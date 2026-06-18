# sources/storage-engines/tikv/tests/integrations/pd/mod.rs

Purpose: registers PD client integration-test modules for both the current v2 RPC client and the legacy RPC client.

Important APIs and declarations: `mod test_rpc_client;` and `mod test_rpc_client_legacy;` include the two PD client suites.

Control flow: Rust test discovery compiles both modules under the integration-test crate. No executable code exists in this file.

State and persistence: none locally. Child modules create mock PD servers, gRPC clients, feature gates, and retry/reconnect state.

Dependencies and integration points: this file is the boundary between the root integration module and PD-specific test suites. It intentionally keeps v2 and legacy coverage side by side so behavior can be compared across APIs.

Risks: omitting either module would silently drop a large compatibility lane. Keeping both modules registered matters while legacy client behavior remains supported or tested.

Test signals: compile/test discovery for both PD suites.
