# sources/test-tools/xfstests-bld/selftests/ltm-kcs

- Purpose: LTM/KCS integration selftest; it starts LTM/KCS infrastructure, submits a kernel build/test request, and checks GCS/result artifacts. The file is 132 lines/2975 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/ltm-kcs`.
- Important APIs/types/functions: shell variables include NO_ACTION, GCE_XFSTESTS, DATECODE, GCE_TEST_VMS, LTM_TEST_FILE, GS_BUCKET, GS_PREFIX; functions include top-level script logic.
- Control flow: sources selftest helpers, launches or contacts LTM/KCS services, submits work, polls GCS/server state, and tears down or verifies artifacts according to the scenario.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
