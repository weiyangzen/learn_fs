<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testhelpers.sh -->
# sources/sync-backup/git-lfs/t/testhelpers.sh

Purpose: large shared helper library for Git LFS shell integration tests, providing pointer/object assertions, remote setup, credentials, server lifecycle, version comparisons, path utilities, symlink support, SSH packet helpers, and lock/server helpers.

Important APIs/functions: includes `assert_pointer`, `refute_pointer`, `local_object_path`, `assert_local_object`, `refute_local_object`, `delete_local_object`, `corrupt_local_object`, server object helpers, lock helpers, `assert_attributes_count`, worktree cleanliness helpers, `pointer`, `wait_for_file`, remote/clone setup functions, `repo_endpoint`, credential setup, `setup`, `shutdown`, `tap_show_plan`, `compare_version`, `calc_oid`, `get_date`, path escaping/canonicalization, symlink helpers, extension setup, `setup_pure_ssh`, `ssh_remote`, packet-line helpers, and `setup_expected_concurrent_transfers`.

Control flow: assertion helpers generally compute paths or query the test server and exit nonzero on mismatch. `setup` initializes the remote server via `lfstest-count-tests`, waits for URL/cert files, creates fake HOME config and credentials, and prints diagnostic environment lines. `shutdown` decrements server usage and removes temp directories when allowed. Remote helpers create bare repositories and clone them with the test credential helper.

State and persistence: owns `REMOTEDIR`, credentials under `remote/creds`, fake HOME `.gitconfig`, test server counters, bare remotes, local clones, local and remote `.git/lfs/objects`, generated logs, and optional symlink/environment state.

Dependencies and integration points: integrates with `curl`, the lfstest Git server, custom test binaries, Git config, credential helpers, SSH transfer proxy, filesystem permissions, and every `t-*.sh` script.

Risks: helper bugs can invalidate many tests at once. Server object checks depend on test-server API stability; path helpers must preserve Windows and POSIX behavior; cleanup must avoid deleting user paths; assertions often use shell greps and must remain quoting-safe.

Test signals: indirectly exercised throughout the integration suite. Individual helpers are validated by the many tests that assert pointers, locks, objects, attributes, credentials, symlinks, remotes, and pure SSH transfer behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testhelpers.sh -->
