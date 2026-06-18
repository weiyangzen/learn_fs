# sources/security-integrity/gocryptfs/internal/configfile/config_test/StrangeFeature.conf

Purpose: This fixture includes an unknown or unsupported feature flag to verify defensive config validation.

Important fields: It resembles a normal config but contains a feature flag not recognized by current code.

Control flow and state: Static fixture; loading should fail validation rather than silently mounting an unsupported format.

Dependencies and integration points: Used by `TestLoadV2StrangeFeature` and feature validation logic.

Risks and test signals: This protects forward compatibility: unknown feature flags must fail closed. Signal is a predictable load error with the deprecated/unsupported filesystem exit classification.
