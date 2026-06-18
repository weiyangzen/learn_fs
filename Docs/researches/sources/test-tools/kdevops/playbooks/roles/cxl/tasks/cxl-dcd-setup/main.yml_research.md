<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-dcd-setup/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-dcd-setup/main.yml

Source read: complete file, 65 lines, 2079 bytes, sha256 `bfed3af047c6bbb2`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-dcd-setup/main.yml_research.md`.

Purpose: add QEMU CXL dynamic capacity extents, create a DAX device for the region, reconfigure it as system RAM, and show resulting memory.

Important APIs/types/functions: delegated localhost shell building QMP JSON and sending it with `ncat`, `ls` of CXL sysfs, `daxctl create-device`, `daxctl reconfigure-device --mode=system-ram --no-online`, `daxctl online-memory`, `lsmem`, and debug outputs.

Control flow: parse QMP port from `qmp_port_str`; send `qmp_capabilities` and `cxl-add-dynamic-capacity`; show region sysfs; create DAX device for `region0`; list `/dev/dax*`; convert `dax0.1` to system RAM and online it; display memory layout.

State and persistence behavior: mutates QEMU device state, kernel CXL region state, DAX device state, and online memory state. Effects last for the VM runtime.

Dependencies and integration: included when DCD is enabled, after the DC region exists. Requires QMP listener, `ncat`, daxctl, kernel CXL DCD support, and expected device names.

Risks: QMP JSON is manually shell-quoted and sizes are hard-coded. `dax0.1` and `region0` assumptions can break if device numbering changes. Some commands use shell without robust failure checking.

Test signals: QMP command should report success, `daxctl list` or `/dev/dax*` should show the new device, `lsmem` should show newly onlined memory, and repeated runs should be tested for idempotence failures.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-dcd-setup/main.yml -->
