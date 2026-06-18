# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-netapp.rules.in

- Purpose: vendor udev policy for NetApp NVMe-oF devices.
- Behavior: sets ONTAP subsystem `iopolicy=queue-depth`, E-Series `iopolicy=round-robin`, and TCP ONTAP controller `ctrl_loss_tmo=-1`.
