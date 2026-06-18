# sources/sync-backup/git-lfs/locking/ssh.go

Purpose: adapts the locking `lockClient` interface to the pure SSH Git LFS transfer protocol using pkt-line commands instead of HTTP.

Important APIs/types/functions: `sshLockClient`, `connection`, `parseLockResponse`, `owner`, `lockData`, `parseListLockResponse`, `Lock`, `Unlock`, `Search`, and `SearchVerifiable`.

Control flow: each public method obtains transfer connection 0, locks the connection mutex, sends a pkt-line command (`lock`, `unlock <id>`, or `list-lock`), reads status/args/lines, and converts protocol data into the same response structs used by HTTP. Lock responses parse key-value args for id, path, owner name, and RFC3339 timestamp. List responses parse `lock`, `path`, `owner`, `ownername`, and `locked-at` lines, plus `next-cursor` args.

State/persistence behavior: the SSH client itself stores only a pointer to `ssh.SSHTransfer`; lock state remains server-side and is cached by `locks.go`.

Dependencies/integration: integrates with `github.com/git-lfs/git-lfs/v3/ssh` `PktlineConnection`, `git.Ref`, shared response types, and translated errors.

Risks: list parsing is order-sensitive and rejects interspersed or incomplete lock data. A map is used before returning locks, so all-lock ordering is not guaranteed. The `force` unlock flag is accepted by the interface but not encoded in this SSH command implementation.

Test signals: coverage is mostly indirect through SSH transfer/integration tests and locking API parity. Parser regressions would surface as protocol errors or missing locks.
