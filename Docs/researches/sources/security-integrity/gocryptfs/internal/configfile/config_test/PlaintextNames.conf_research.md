# sources/security-integrity/gocryptfs/internal/configfile/config_test/PlaintextNames.conf

Purpose: This fixture represents a gocryptfs config with plaintext filename mode enabled.

Important fields: It stores version/creator metadata, encrypted master key, scrypt parameters, and feature flags that include plaintext-name behavior while omitting encrypted-name features such as diriv/longnames.

Control flow and state: Static persistent config fixture only. Tests load/decrypt it with known credentials.

Dependencies and integration points: Used by config tests to verify plaintext-name feature flag interpretation and creation/loading compatibility.

Risks and test signals: Fixture must remain synchronized with expected password and feature assertions. Signals are successful decrypt and correct plaintext-name mode detection.
