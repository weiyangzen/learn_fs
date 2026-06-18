# sources/sync-backup/git-lfs/t/cmd/lfs-ssh-echo.go

Purpose: fake SSH executable for integration tests, emulating SSH argument parsing, multiplex control path checks, Git command forwarding, and LFS auth JSON responses.

Important APIs/types/functions: `sshResponse`, `shell`, `spawnCommand`, `checkSufficientArgs`, and `main`.

Control flow: parses optional OpenSSH control-master/control-path args, optional `-p`, optional `--`, validates host `git@127.0.0.1`, then inspects the remote command. `git-lfs-transfer`, `git-upload-pack`, and `git-receive-pack` are executed through a shell. `git-lfs-authenticate` returns JSON with an LFS href and optional expired `expires_at`/`expires_in` for special repos.

State/persistence behavior: creates/removes a control path file for multiplex master mode and reads no persistent repo state directly except through spawned commands.

Dependencies/integration: validates SSH command construction, auth endpoint generation, transfer protocol, and multiplexing behavior.

Risks: relies on positional args; malformed input exits with diagnostic. Shell execution is acceptable here because the tool is test-only.

Test signals: exact stderr errors, generated JSON, and successful forwarded Git/LFS subprocess execution.
