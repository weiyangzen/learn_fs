# sources/sync-backup/git-lfs/t/t-alternates.sh

## Purpose
Integration tests for Git object alternates as they affect Git LFS object discovery. The script ensures LFS fetch and push avoid unnecessary batch requests when required objects are available through alternate Git object directories.

## Important APIs, Functions, and Control Flow
Each `begin_test` creates or clones a repository with one LFS-tracked file, removes local `.git/lfs/objects`, configures alternates either through `.git/objects/info/alternates` or `GIT_ALTERNATE_OBJECT_DIRECTORIES`, and runs `git lfs fetch` or push. Cases cover single alternate, multiple alternates with stale entries, commented alternate entries, quoted alternate paths, and environment variable alternates.

## State, Persistence, and Dependencies
The tests manipulate the local Git object store, LFS object store, alternates file, and environment variables. They depend on `setup_remote_repo_with_file`, `clone_repo`, `native_path`, and `native_path_list_separator` from `testlib.sh`. Windows path handling is explicitly considered for quoted alternates.

## Integration Points, Risks, and Test Signals
The key signal is whether trace output contains `sending batch of size 1`; a count of zero means LFS resolved the object locally through alternates. Commented alternates should be ignored and therefore trigger a batch request. Risks include trace-string fragility, path quoting differences across platforms, and hidden dependency on Git's alternates file parsing semantics.
