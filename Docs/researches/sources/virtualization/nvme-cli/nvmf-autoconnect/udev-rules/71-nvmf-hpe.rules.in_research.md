# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/71-nvmf-hpe.rules.in

- Purpose: vendor udev policy for HPE Alletra NVMe-oF devices.
- Behavior: sets `iopolicy=round-robin` for HPE Alletra NVM subsystems and `ctrl_loss_tmo=-1` for matching TCP controllers.
