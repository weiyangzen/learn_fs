# sources/test-tools/xfstests-bld/selftests/config

- Purpose: selftest default configuration; it sets baseline primary filesystem, kernel source path, and distribution knobs for the selftest scripts. The file is 21 lines/436 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/config`.
- Important APIs/types/functions: shell variables include PRIMARY_FSTYPE, KSRC, DISTRO; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
