## sources/test-tools/kdevops/workflows/ltp/Kconfig

Purpose: Configures Linux Test Project workflow groups and repository source/ref.

Important APIs/types/functions: Test group symbols include `LTP_TESTS_CVE`, `FCNTL`, `FS`, `FS_BIND`, `FS_PERMS_SIMPLE`, `FS_READONLY`, `NFS`, `NOTIFY`, `RPC`, `SMACK`, and `TIRPC`. Repo symbols include `HAVE_MIRROR_LTP`, `LTP_REPO_CUSTOM`, `LTP_REPO_URL`, `LTP_REPO`, and `LTP_REPO_COMMIT`.

Control flow: Dedicated workflow mode exposes test group selections. Repo source defaults to a mirror when present or default upstream otherwise, with custom URL override support.

State and persistence: Kconfig selections persist to `.config`; Makefile turns them into `LTP_ARGS` and group lists.

Dependencies and integration points: Uses libvirt mirror detection and default LTP URL constants. Integrated with `ltp.yml` Ansible playbook.

Risks and test signals: Default commit is pinned to `20240129`; users expecting latest LTP need to update it. Test by inspecting generated `ltp_repo`/`ltp_repo_commit` and selected group vars.
