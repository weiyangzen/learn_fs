# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-vastdata.rules.in

- Purpose: vendor udev policy for VAST Data NVMe-oF devices.
- Behavior: sets NVM subsystem `iopolicy=round-robin` and controller `ctrl_loss_tmo=-1` for model `VASTData`.
