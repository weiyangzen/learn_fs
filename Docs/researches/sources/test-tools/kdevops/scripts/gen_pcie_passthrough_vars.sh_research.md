<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/gen_pcie_passthrough_vars.sh -->
# sources/test-tools/kdevops/scripts/gen_pcie_passthrough_vars.sh

Purpose: emits YAML-style `pcie_passthrough_devices` entries from dynamic Kconfig variables for libvirt PCIe passthrough.

Important APIs and functions: sources `${TOPDIR}/.config` and `${TOPDIR}/scripts/lib.sh`; uses `CONFIG_KDEVOPS_DYNAMIC_PCIE_PASSTHROUGH_NUM_DEVICES`, per-device `CONFIG_KDEVOPS_DYNAMIC_PCIE_PASSTHROUGH_####_*` variables, and passthrough target mode config.

Control flow: fail if device count is empty, print the list header, load `vfio-pci`, adjust group and permissions on `/sys/bus/pci/drivers_probe`, iterate configured device slots, evaluate enabled entries, collect fields with `eval`, decide target guest, and echo inline YAML objects.

State and persistence: changes kernel module state by loading `vfio-pci` and changes ownership/mode of `/sys/bus/pci/drivers_probe`. It writes only to stdout for vars generation.

Dependencies and integration: bash, sudo, modprobe, seq, kdevops `.config`, and dynamic PCI Kconfig Makefile integration where output is appended to extra vars.

Risks: heavy use of `eval` on config-derived variable names requires trusted config. Unquoted variables can break on spaces. Sudo operations may prompt or fail in noninteractive runs. Test signals include a stub `.config` in a disposable environment, shellcheck, validation of generated YAML with enabled/disabled devices, and failure when device count is missing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/gen_pcie_passthrough_vars.sh -->
