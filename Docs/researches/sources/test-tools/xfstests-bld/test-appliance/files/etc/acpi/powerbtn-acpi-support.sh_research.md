# sources/test-tools/xfstests-bld/test-appliance/files/etc/acpi/powerbtn-acpi-support.sh

- Purpose: ACPI power button handler; it logs ACPI power button events and initiates shutdown behavior in the appliance. The file is 19 lines/454 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/acpi/powerbtn-acpi-support.sh`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
