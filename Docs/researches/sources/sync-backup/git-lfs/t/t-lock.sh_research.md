# sources/sync-backup/git-lfs/t/t-lock.sh

## Purpose

Tests creating Git LFS locks across branch-ref requirements, remote selection, multiple paths, JSON output, absolute paths, client certificate auth, nonexistent files, duplicate locks, directories, nested paths, subdirectories, symlinked workdirs, ignored lockable files, and pure SSH transfer locking.

## Important APIs, control flow, and dependencies

The script uses `setup_remote_repo_with_file`, `clone_repo`, `setup_pure_ssh`, `git lfs lock`, `git lfs unlock`, `git lfs locks`, `assert_lock`, `assert_server_lock`, `assert_server_lock_ssh`, branch config (`push.default`, `branch.main.merge`, `remote.pushDefault`, `branch.main.pushRemote`), client cert config, `.gitattributes lockable`, `.gitignore`, symlink helpers, and `GIT_TRACE_PACKET`.

## State, dependencies, integration points, risks, and test signals

State includes server lock records keyed by path/ref, local branch/remote config, lockable file permissions, ignored-file config, client cert files, and SSH URL config. Integration points are locks API, ref validation, push remote precedence, path canonicalization, JSON formatting, local checkout permission updates, TLS client auth, and pure SSH protocol. Risks include locking against the wrong branch, failing to normalize absolute/subdirectory/symlink paths, permitting directory locks, or breaking lockable ignored files. Signals are JSON assertions, server lock/ref checks, output greps, nonzero failure checks, and writeability assertions.
