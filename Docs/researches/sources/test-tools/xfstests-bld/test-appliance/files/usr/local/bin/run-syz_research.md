# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/run-syz

- Purpose: syzkaller repro runner; it runs syzkaller repro tests under the xfstests syz harness inside the appliance. The file is 75 lines/1174 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/run-syz`.
- Important APIs/types/functions: shell variables include DIR; functions include top-level script logic.
- Control flow: sources appliance config/utilities, prepares result directories and runner options, invokes the target test harness, copies/merges xUnit output, summarizes results, and writes `/tmp/retdir/exit_code`.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
