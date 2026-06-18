# sources/user-network-fs/rclone/fs/backend_config_test.go

Purpose: unit tests the small pure helpers in `backend_config.go` that are critical for serializing state and filtering provider-specific options.

Important APIs/functions: `TestStatePush` validates empty and non-empty state stacking, including escaping commas in pushed values as Unicode wide commas. `TestStatePop` validates decoding, empty values, final-element handling, and wide-comma restoration. `TestMatchProvider` validates blank-provider permissiveness, exact provider membership, and negated membership lists.

Control flow: each test is table-driven or assertion-driven over pure functions. No config storage, registry, or OAuth setup is needed.

State and persistence behavior: the tests document the state encoding contract used by `configAll` and OAuth return-state stacking. Correct escaping is important because state fields are comma-separated and may themselves contain commas.

Dependencies and integration points: uses `testify/assert`. It constrains behavior used by `BackendConfig`, provider-specific option filtering, and config state handoff through API/UI frontends.

Risks: tests do not cover malformed deeply nested state, `BackendConfig` loop behavior, choice overrides, edit defaults, or OAuth routing. They do catch regressions in the primitive encoding/matching behavior.

Test signals: focused and deterministic coverage for pure helper functions.
