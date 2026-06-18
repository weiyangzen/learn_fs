# sources/sync-backup/git-lfs/lfsapi/lfsapi.go

Purpose: Defines the high-level LFS API client composition, endpoint and credential dependencies, and pure SSH transfer lifecycle.

Important APIs/types/functions: `Client`, `NewClient`, `Context`, `SSHTransfer`, `initSSHTransfer`, and `closeSSHTransfers`.

Control flow: `NewClient` creates a default context if needed, builds endpoint finder, HTTP client, credential helper context, access-mode list, and SSH transfer map. `SSHTransfer` memoizes per operation/remote transfer objects and initializes them lazily. `initSSHTransfer` checks endpoint SSH metadata and `lfs.<url>.sshtransfer` config before attempting `ssh.NewSSHTransfer`.

State and persistence behavior: Holds mutable endpoint/access state, credential helper, HTTP client cache, and SSH transfer map protected by a mutex. `closeSSHTransfers` shuts down all live transfers and clears the map.

Dependencies and integration points: Integrates `lfshttp`, `creds`, `config.URLConfig`, `ssh.SSHTransfer`, and tracer logging. Locking code uses this to choose HTTP versus pure SSH lock clients.

Risks and edge cases: A failed SSH transfer initialization is not cached, so repeated calls may retry. Config values other than `negotiate` or `always` disable pure SSH transfer. Concurrency depends on the transfer mutex.

Test signals: Indirect coverage through locking generic client behavior and endpoint tests. No direct test for transfer shutdown errors in this subset.
