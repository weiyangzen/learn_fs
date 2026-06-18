# sources/sync-backup/borg/docs/usage/general/file-systems.rst.inc

Purpose: documents repository filesystem recommendations and the Borg 2 storage model based on `borgstore`.

Important APIs and control flow: recommends reliable journaling filesystems and explains that Borg uses `borgstore` as a key/value repository store, currently via `file:` posixfs locally or over SSH through `borg serve`, storing each chunk as a separate filesystem file in a nested layout.

State and persistence: repository data is persisted as many filesystem objects instead of Borg 1.x segment files.

Dependencies and integration points: borgstore backends, `file:`, SSH/remote `borg serve`, future `sftp:`/`rclone:` style backend possibilities, compact behavior, locking, and repository index behavior.

Risks: many files increase filesystem overhead and can reduce performance on filesystems with poor small-file/random-I/O behavior. Space overhead depends on allocation block strategy.

Test signals: repository creation/access on supported filesystems, high-object-count scalability, compact deleting individual chunks, remote borgstore access, and backend conformance tests.
