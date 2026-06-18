# sources/sync-backup/borg/src/borg/testsuite/archiver/disk_full_test.py

Purpose: slow stress test for Borg behavior when the repository filesystem fills up. It requires a separately mounted writable 700 MB filesystem at `/tmp/borg-mount`.

Important APIs/types/functions: `DF_MOUNT` names the required mount. `make_files` rebuilds an input directory with a random number and size of random files. `test_disk_full` is parametrized for ten passes and uses `cmd_fixture` to run a Borg executable-style command path.

Control flow: the test skips unless `DF_MOUNT` exists. For each pass it sets confirmation environment variables, removes old repo/input directories, creates an unencrypted repo, then loops creating random input files and archives until file creation or `borg create` fails from ENOSPC. It forcibly removes old lock directories after each create attempt, deletes input to free space, runs `repo-list`, repairs with `check --repair`, asserts repair success, and finally deletes the repository to free disk.

State and persistence behavior: intentionally fills the mounted filesystem with repository and input data, leaves partial archives/objects after ENOSPC, removes lock directories, and runs repair. It mutates environment variables and performs cleanup in `finally`.

Dependencies and integration points: covers repo-create, create, lock cleanup, repo-list, check repair, repo-delete, and filesystem ENOSPC handling. Depends on external mount provisioning and enough permissions.

Risks: very resource-heavy and slow; incorrect mount selection could fill a real filesystem. Manual lock directory removal references older lock paths and may not align with newer store-locking internals. Random inputs make exact failure point nondeterministic.

Test signals: validates Borg can recover to a repairable repository state after disk-full failures and does not leave unrecoverable locks.
