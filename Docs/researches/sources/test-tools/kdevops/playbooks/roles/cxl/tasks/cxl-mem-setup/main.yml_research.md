<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-mem-setup/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-mem-setup/main.yml

Source read: complete file, 21 lines, 692 bytes, sha256 `68f3a1bd853044c0`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-mem-setup/main.yml_research.md`.

Purpose: configure ordinary CXL memory as a DAX namespace, convert it to system RAM, and online it.

Important APIs/types/functions: `cxl create-region -m -d decoder0.0 -w 1 mem0 -s 256M`, `ndctl create-namespace -m dax -r region0`, `daxctl reconfigure-device --mode=system-ram --no-online dax0.0`, and `daxctl online-memory dax0.0`.

Control flow: create CXL region, create DAX namespace, reconfigure the dax device as system RAM without auto-online, then online memory explicitly.

State and persistence behavior: mutates CXL region/namespace and memory hotplug state in the running system.

Dependencies and integration: included from CXL main when `kdevops_enable_cxl_dcd` is false. Assumes decoder `decoder0.0`, endpoint `mem0`, `region0`, and `dax0.0`.

Risks: hard-coded topology/device names and no idempotence guards mean reruns can fail after the region or namespace already exists. Commands are privileged and alter memory layout.

Test signals: `cxl list`, `ndctl list`, `daxctl list`, and `lsmem` should reflect region0/dax0.0 and online memory after the task.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-mem-setup/main.yml -->
