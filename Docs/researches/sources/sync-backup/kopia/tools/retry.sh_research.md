# sources/sync-backup/kopia/tools/retry.sh

Purpose: small POSIX-shell wrapper to retry a command up to three times.

Control flow/APIs: loops attempts 1, 2, and 3, echoes the command and attempt number, executes `"$@"`, exits 0 on first success, and exits 1 if all attempts fail.

State/persistence: no direct persistence; all side effects come from the wrapped command and may happen multiple times.

Dependencies/integration: used from `tools.mk` as `retry` on non-Windows platforms to make transient build/download commands more robust.

Risks/test signals: there is no sleep/backoff and no distinction between retryable and non-retryable failures. The wrapped command must be idempotent or tolerate repeated execution. Behavior is simple enough to be covered by users of the wrapper rather than its own tests.
