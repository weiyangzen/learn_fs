# sources/sync-backup/git-lfs/t/cmd/lfs-askpass.go

Purpose: deterministic askpass helper for integration tests.

Important API: `main`.

Control flow: joins prompt args, returns username when prompt contains `Username`, password when prompt contains `Password`, and allows overrides via `LFS_ASKPASS_USERNAME` and `LFS_ASKPASS_PASSWORD`.

State/persistence behavior: reads environment only; no persistence.

Dependencies/integration: used by tests that exercise Git credential prompts or HTTP auth fallback.

Risks: prompt matching is substring-based and case-sensitive.

Test signals: stdout contains the selected answer.
