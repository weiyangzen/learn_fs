# sources/user-network-fs/rclone/backend/sftp/stringlock.go

Purpose: provides a keyed mutex used by the SFTP backend to serialize operations for the same path, notably recursive directory creation.

Important APIs/types/functions: `stringLock` stores a global mutex and a map from string IDs to channels. `newStringLock` initializes the map. `Lock(ID)` waits while a channel exists for the ID, then installs a new channel. `Unlock(ID)` closes and removes the channel, panicking if the ID was not locked.

Control flow: waiters release the global mutex before blocking on the per-ID channel, then re-check the map after wakeup. Different IDs can proceed independently; same-ID callers serialize.

State and persistence behavior: all state is in-memory and scoped to one `Fs` instance. Channels act as one-shot broadcast notifications on unlock.

Dependencies/integration: uses only `sync`. `sftp.go` uses this for `mkdir` to avoid concurrent creators racing on the same directory tree.

Risks/test signals: improper unlock order or missing unlock can deadlock same-ID operations; unlocking an unknown ID intentionally panics. `stringlock_test.go` stress-tests per-key serialization.
