# sources/test-tools/kdevops/docs/virt-install-demo.sh

Purpose: demonstration shell script for creating a custom libvirt guest using `virt-install`, a downloaded ISO, and a qcow2 disk image. It is documentation/example code rather than a production role.

Important APIs/types/functions: variables define `ISO_URL`, `REL`, `DATE_SHORT`, `DISK_BUS`, `MEM`, `CPUS`, `QCOW2_SIZE`, `VIRT_NAME`, `ISO_DIR`, `QCOW2_DIR`, and derived paths. Functions are `set_qcow2`, `get_iso`, and `custom_virt_install`; external commands are `qemu-img`, `wget`, `virt-install`, `date`, and `basename`.

Control flow: compute image and ISO paths, create a qcow2 if missing, download the ISO if missing, then call `virt-install` with default network, serial console, qcow2 disk, `--location`, kernel console args, and OS variant equal to `REL`.

State/persistence behavior: creates persistent files under `images/<REL>/` and `isos/<REL>/`, and registers a libvirt domain named `${USER}-${REL}`. Re-running reuses existing ISO and qcow2 paths for the same date rather than rebuilding them.

Dependencies/integration: integrates with the libvirt/QEMU toolchain and the broader kdevops bring-up documentation. It does not use Ansible variables or inventory.

Risks/test signals: `--location` appears twice, variables are unquoted in command arguments, `ISO_URL` is a placeholder, and the script assumes a serial-installable distribution. Test signals are successful image creation, ISO download, domain definition/start, and boot progress on the serial console.
