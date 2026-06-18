# sources/test-tools/xfstests-bld/selftests/util/ltm

- Purpose: selftest LTM helper library; it waits for LTM readiness, queries management state, shuts down or relaunches LTM, and detects whether it is managing tests. The file is 133 lines/2835 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/util/ltm`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include wait_ltm_online, get_ltm_info, ltm_managing_tests, shutdown_ltm, relaunch_ltm.
- Control flow: sources selftest helpers, launches or contacts LTM/KCS services, submits work, polls GCS/server state, and tears down or verifies artifacts according to the scenario.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
