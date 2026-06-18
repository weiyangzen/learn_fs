## sources/user-network-fs/gcsfuse/cfg/optimize_test.go

Purpose: Tests generic optimization machinery and metadata lookup behavior.

Important APIs/types/functions: helpers `defaultConfig`, `createTestServer`, `closeTestServer`, `resetMetadataEndpoints`, and `isFlagPresentInOptimizationResults`; tests for `getMachineType`, `ApplyOptimizations`, and `CreateHierarchicalOptimizedFlags`.

Control flow: metadata tests replace `metadataEndpoints` with httptest servers returning errors, quota-style failures, or machine-type paths. Apply tests configure default config, optional disabled autoconfig or user-set Viper flags, call `ApplyOptimizations`, and assert mutated fields. Hierarchical tests compare nested maps and reject key-prefix conflicts.

State and persistence: mutates package-global `metadataEndpoints` and resets it; no persistent state.

Dependencies and integration points: uses `httptest`, Viper, testify assert/require, reflection, and generated optimization rules.

Risks: global endpoint mutation would be unsafe if these tests run in parallel. Tests do not verify actual HTTP request header contents. The quota test succeeds on the second retry, covering retry count but not multiple endpoints.

Test signals: high-value regression coverage for machine metadata handling, autoconfig disabling, optimization application, user override preservation, and optimized flag serialization shape.
