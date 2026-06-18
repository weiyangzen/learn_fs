# sources/sync-backup/git-lfs/t/t-object-authenticated.sh

Purpose: checks that uploading an LFS object to an authenticated remote path works when terminal prompts are disabled, which exercises credential handling in noninteractive environments.

Important APIs/functions: uses `ensure_git_version_isnt` to require Git 2.3 or newer for `GIT_TERMINAL_PROMPT`, plus `setup_remote_repo`, `clone_repo`, `git lfs track`, `git commit`, and `git lfs push`.

Control flow: the test creates and clones a remote named from the script, tracks `*.dat`, writes `hi.dat`, commits `.gitattributes` and the file, then runs `GIT_CURL_VERBOSE=1 GIT_TERMINAL_PROMPT=0 git lfs push origin main`.

State/persistence behavior: the repository gains one LFS-tracked blob and its pointer commit. The remote LFS store should receive the object without needing interactive credential prompts.

Dependencies/integration points: integrates Git credential behavior, HTTP/curl verbosity, test server authentication defaults, LFS batch upload, and noninteractive environment variables.

Risks/test signals: the test has no explicit object assertion; command success is the signal. A failure usually points to authentication prompt leakage, missing credentials, or transfer setup regressions.
