# sources/security-integrity/gocryptfs/internal/configfile/validate.go

Purpose: This file validates `ConfFile` combinations before loading, using, or writing config files.

Important APIs and functions: `ConfFile.Validate()` checks on-disk version, encrypted key presence/length, scrypt parameters, known feature flags, mutually incompatible feature combinations, required fields such as FIDO2 params, and long-name constraints.

Control flow and state: Validation is read-only over the config object and returns errors for unsupported or inconsistent state. It is called during `Create`, `Load`, `WriteFile`, and `ContentEncryption`.

Dependencies and integration points: Serves as the compatibility/security gate for all config consumers.

Risks and test signals: Overly permissive validation can mount unsupported filesystems; overly strict validation can strand valid users. Signals include fixture tests for v1 rejection, unknown feature rejection, and generated config validation.
