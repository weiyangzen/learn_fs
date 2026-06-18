# sources/user-network-fs/rclone/backend/alias/alias_internal_test.go

Purpose: Tests alias backend path resolution and error handling against the local backend.

Important APIs/types/functions: `prepare` installs config and sets `TestAlias` type/remote. `TestNewFS` table-drives combinations of configured remote root, requested Fs root, and list path, asserting entry names, sizes, and directory flags. `TestNewFSNoRemote` and `TestNewFSInvalidRemote` assert construction errors.

Control flow: Each table row converts fixture paths under `test/files` to absolute local paths, configures alias, opens `TestAlias:<fsRoot>`, lists `fsList`, sorts entries, and compares with expected entries.

State and persistence: Mutates test rclone config via `configfile.Install` and `config.FileSetValue`. Reads local fixture files; no persistent writes.

Dependencies and integration points: Imports local backend for registration, rclone config APIs, `fs.NewFs`, and testify `require`.

Risks: Tests rely on fixture layout and local path semantics, including `..` traversal behavior. They do not cover alias cycle chains.

Test signals: Provides focused validation that alias preserves list paths and rejects absent/invalid target config.
