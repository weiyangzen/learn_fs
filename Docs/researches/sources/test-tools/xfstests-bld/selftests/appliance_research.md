# sources/test-tools/xfstests-bld/selftests/appliance

- Purpose: selftest appliance orchestration script; it builds architecture-specific appliances, optionally launches KVM/GCE smoke runs, and verifies artifacts for amd64/i386/arm64 paths. The file is 206 lines/4493 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/appliance`.
- Important APIs/types/functions: shell variables include ALL_LIST, DATECODE, LIST, SKIP_BUILD, SKIP_TEST, SKIP_ARM_QEMU_TEST, KSRC, KSRC_EXPLICIT, NO_ACTION, SKIP_GCE, SKIP_QEMU, GCE_TEST_VMS, GCE_XFSTESTS; functions include build_appliance.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
