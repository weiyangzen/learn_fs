# sources/sync-backup/restic/cmd/restic/cmd_forget_test.go

Purpose: unit tests for forget option parsing and host filter defaulting.

Important tests: `TestForgetPolicyValues` validates numeric, unlimited, empty, negative, and non-numeric values for `ForgetPolicyCount`. `TestForgetOptionValues` validates allowed and rejected negative keep counts and `keep-within` durations. `TestForgetHostnameDefaulting` verifies `RESTIC_HOST` defaulting, `--host` override, and empty `--host` clearing.

State/persistence: uses environment variable mutation through `t.Setenv` and local pflag parsing only; no repository mutation.

Dependencies/integration: `data.ParseDurationOrPanic`, `pflag`, snapshot filter finalization, and `rtest`.

Risks/test signals: protects destructive-command validation paths before repository access. Does not test actual deletion; integration file handles safety-net deletion behavior.
