# sources/security-integrity/cryfs/crates/check/src/node_info/mod.rs

Purpose: This module root defines the public facade for checker node/blob reference and observation types.

Important APIs and flow: It declares and reexports blob observation, maybe blob observation, blob reference, blob reference with id, maybe blob reference with id, node observation, maybe node observation, node reference, combined node/blob reference, and reachable combined reference modules.

State and persistence: It owns no state. It organizes value types that carry checker traversal context into errors and public APIs.

Dependencies and integration: `lib.rs` reexports these types for tests and callers. The runner, checks, display helpers, and error types all import through this module.

Risks and test signals: These reexports form a stable type vocabulary for expected test errors. Changes to variant names or structure would have broad impact across integration tests.
