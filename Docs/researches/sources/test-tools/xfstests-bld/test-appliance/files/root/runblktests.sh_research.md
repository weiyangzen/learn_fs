# sources/test-tools/xfstests-bld/test-appliance/files/root/runblktests.sh

- Purpose: blktests appliance runner; it sets up appliance context, runs blktests suites with repeat support, and writes result/exit status artifacts. The file is 87 lines/1502 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/runblktests.sh`.
- Important APIs/types/functions: shell variables include API_MAJOR, API_MINOR, RPT_COUNT; functions include top-level script logic.
- Control flow: sources appliance config/utilities, prepares result directories and runner options, invokes the target test harness, copies/merges xUnit output, summarizes results, and writes `/tmp/retdir/exit_code`.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
