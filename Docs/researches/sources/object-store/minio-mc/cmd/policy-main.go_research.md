# Research: sources/object-store/minio-mc/cmd/policy-main.go

## sources/object-store/minio-mc/cmd/policy-main.go

Purpose: retains a hidden legacy `mc policy` command that redirects users to `mc anonymous`.

Important APIs and functions: `policyFlags` keeps a legacy recursive flag; `policyCmd` is hidden and has a help template saying to use `mc anonymous`; `mainPolicy` prints the same guidance.

Control flow: invocation does not perform policy work. It runs global setup, then `mainPolicy` emits an informational line and returns nil.

State and persistence: no object-store or local-state mutation.

Dependencies and integration: exists in `appCmds` for compatibility and uses shared CLI/global flag plumbing and console output.

Risks and tests: command is intentionally minimal. Scripts expecting old `mc policy` behavior will not get functional policy management here, only guidance. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/policy-main.go -->
