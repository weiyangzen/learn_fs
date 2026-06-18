# sources/object-store/minio-mc/cmd/config-utils.go

Purpose: Provides small validators and URL normalization helpers used by alias/config parsing and validation.

Important APIs/types/functions: `validAPIs`, `accessKeyMinLen`, `secretKeyMinLen`, `isValidAccessKey`, `isValidSecretKey`, `trimTrailingSeparator`, `isValidHostURL`, `isValidAPI`, `isValidLookup`, and `isValidPath`.

Control flow: Validation is mostly whitelist and minimum-length checks. Empty access/secret keys are allowed for anonymous endpoints. Host validation delegates parsing to `newClientURL` and accepts only `http` or `https` with root path.

State and persistence: Stateless helpers; no persistent state.

Dependencies/integration: Uses `newClientURL` and Go `slices`/`strings`. Called by config validation and alias setup flows.

Risks: Key validation checks length only, not character classes. `isValidHostURL` intentionally rejects URLs with non-root paths, which is correct for alias hosts but not general object paths.

Test signals: `config-utils_test.go` covers valid/invalid host URL, API names, and key lengths.
