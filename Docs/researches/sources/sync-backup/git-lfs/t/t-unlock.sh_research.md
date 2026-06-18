<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-unlock.sh -->
# sources/sync-backup/git-lfs/t/t-unlock.sh

Purpose: comprehensive integration suite for `git lfs unlock`, covering path/id addressing, ref verification, remote override precedence, multi-file JSON, read-only lockable files, missing/removed paths, validation errors, force behavior, uncommitted/untracked files, and SSH transfer locks.

Important APIs/functions: defines `setup_repo`; uses `setup_remote_repo_with_file`, `git lfs track --lockable`, `git lfs lock`, `git lfs unlock`, `assert_lock`, `assert_server_lock`, `refute_server_lock`, SSH lock helpers, and file writability helpers.

Control flow: initial tests unlock by path or ID under required and non-required refs, including tracked upstream refs. Remote override tests intentionally configure invalid `remote.pushDefault` or `branch.main.pushRemote` and prove `--remote origin` wins. Bad-ref tests ensure lock remains when refs mismatch. Later cases cover multiple file unlock, JSON output, read-only transitions, removed/nonexistent/unlockable files, missing arguments, ambiguous id+path arguments, uncommitted modifications with and without `--force`, untracked files, and pure SSH `git-lfs-transfer`.

State and persistence: creates lock records on the test server, commits lockable attributes, changes file modes, removes or modifies working-tree files, and changes remote selection config.

Dependencies and integration points: integrates with lock API, ref verification, remote resolution, lockable attribute handling, JSON output, local dirty-state checks, and SSH transfer protocol.

Risks: unlock errors can leave server locks orphaned or remove locks from the wrong branch. File mode transitions can make user files unexpectedly read-only or writable, and force/dirty checks guard data loss.

Test signals: more than twenty cases cover path/id unlock, good/bad/tracked refs, remote override, multiple/JSON unlock, read-only behavior, missing paths, errors, dirty/untracked safety, force, and SSH transfer.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-unlock.sh -->
