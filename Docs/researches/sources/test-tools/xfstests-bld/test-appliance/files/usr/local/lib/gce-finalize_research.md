# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize

- Purpose: GCE finalization trigger; it stops the wait loop and launches final shutdown/finalize handling. The file is 11 lines/197 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
