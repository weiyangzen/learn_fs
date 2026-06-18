# sources/test-tools/crashmonkey/vm_scripts/setup.sh

Purpose: large provisioning script for a server that will host multiple CrashMonkey VirtualBox VMs. It installs dependencies, clones CrashMonkey, installs VirtualBox, imports a base VM, clones more VMs, starts them, distributes helper scripts, and updates hostnames.

Important APIs/types/functions: appending `vm_aliases` to `.bashrc`, `apt-get`, `git clone`, VirtualBox `.deb` and extension pack downloads, `VBoxManage import`, `clone_vms.sh`, `start_all_vms.sh`, `scp_remote_scripts_to_vms.sh`, and `trigger_remote_script_update_hostname.sh`.

Control flow: update shell aliases, create `projects`, install packages, clone repo, install filesystem tools and VirtualBox dependencies, install VirtualBox packages/extension pack, import OVA, clone VMs 2-16, export/read `num_vms`, start VMs, sleep, copy scripts, update hostnames, and print completion.

State/persistence behavior: heavily mutates the host system, home directory, bashrc, installed packages, VirtualBox registry, and VM state. Dependencies/integration: assumes Ubuntu/Xenial-era package names, an OVA in home, scripts in the current directory, and passwordless/interactive sudo as needed.

Risks/test signals: highly environment-specific, appends aliases repeatedly, no `set -e`, hard-coded VirtualBox version, and broad side effects make it unsuitable for unattended reruns without cleanup.
