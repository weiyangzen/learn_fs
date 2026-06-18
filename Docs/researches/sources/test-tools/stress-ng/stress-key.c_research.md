# sources/test-tools/stress-ng/stress-key.c

Purpose: implements `key`, a Linux keyring stressor that creates, searches, reads, updates, links, unlinks, revokes, invalidates, and clears user keys in the process keyring.

Important APIs/types/functions: syscall wrappers `shim_add_key()`, `shim_keyctl()`, and optional `shim_request_key()` exercise keyutils operations. Constants bound each batch to 256 keys, short timeouts, and a large invalid description buffer. The main function tracks `keys_added` for metrics.

Control flow: after allocating a huge random description string, the worker sync-starts and repeatedly fills a key array. For each key index it tries several invalid `add_key()` variants, creates a valid `user` key, optionally sets timeout and searches. It then iterates created keys to describe, update, read, request, get security, chown, query capabilities, set permissions, link/unlink, revoke, and invalidate. It discards `/proc/keys` and `/proc/key-users` caches, issues an invalid `keyctl` command, increments bogo ops, invalidates leftovers, and clears the process keyring.

State and persistence behavior: keys are kernel keyring objects scoped to the process keyring and explicitly invalidated/cleared. The huge description is heap memory. No repository state persists.

Dependencies and integration points: gated on keyutils headers plus `add_key`, `keyctl`, and syscall support; `request_key` is optional. Uses stress-ng random strings, filesystem discard, settings, metrics, and process state. Registered as `CLASS_OS` with always-on verification.

Risks: permissions, key quotas, disabled keyrings, and LSM policy can cause `EPERM`, `EDQUOT`, `ENOMEM`, `EKEYEXPIRED`, or `ENOKEY`. The stressor treats permission or unimplemented syscalls as non-implemented skips but reports unexpected keyctl errors.

Test signals: validate skip on systems without key permissions, successful cleanup of process keyring, meaningful keys-per-second metric, and no quota leakage after forced stop.
