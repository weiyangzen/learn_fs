# sources/test-tools/crashmonkey/vm_scripts/install-4.15.sh

Purpose: downloads and installs Ubuntu mainline Linux kernel 4.15 packages inside a VM/host.

Important APIs/types/functions: `cd /tmp`, three `wget` URLs for headers/image `.deb` files, and `sudo dpkg -i *.deb`. Control flow is linear with no args.

State/persistence behavior: writes packages to `/tmp` and installs kernel packages system-wide. Dependencies/integration: likely used to prepare CrashMonkey test VMs for a target kernel.

Risks/test signals: wildcard `*.deb` installs all debs in `/tmp`, URLs may become unavailable, no checksum verification, and no reboot/default-kernel selection is handled.
