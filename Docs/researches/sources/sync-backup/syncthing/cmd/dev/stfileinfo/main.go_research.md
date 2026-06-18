# sources/sync-backup/syncthing/cmd/dev/stfileinfo/main.go

Purpose: development inspection tool for filesystem metadata and Syncthing block hashing of a single path.

Important APIs/types/functions: flag `-s` selects standard block sizing. It uses `os.Lstat`, optional `os.Stat`, `protocol.MinBlockSize`, `protocol.BlockSize`, and `scanner.Blocks`.

Control flow: validates a path argument, prints cleaned path and lstat size/mode/time. For non-directory non-regular paths, it follows with `Stat` output. For regular files it opens the file, chooses whole-file block size unless `-s` or small size triggers standard Syncthing block sizing, then prints scanner block metadata.

State and persistence behavior: read-only filesystem access. No durable state.

Dependencies/integration: integrates with Syncthing protocol block sizing and scanner hashing logic, making it useful for comparing real filesystem observations with Syncthing index data.

Risks/test signals: large files without `-s` may be hashed as one block, which is intentional but not representative of normal indexing. Signal is metadata plus block list output or fatal error on inaccessible paths.
