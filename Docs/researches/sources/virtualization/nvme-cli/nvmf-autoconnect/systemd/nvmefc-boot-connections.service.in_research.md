# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmefc-boot-connections.service.in

- Purpose: boot-time FC-NVMe discovery service.
- Conditions/order: runs only when `/sys/class/fc/fc_udev_device/nvme_discovery` exists, after udevd and before `local-fs-pre.target`.
- Action: oneshot shell command writes `add` to the FC discovery sysfs node.
- Hardening: enables several systemd sandboxing restrictions such as `ProtectSystem`, `ProtectHome`, `ProtectProc`, `MemoryDenyWriteExecute`, and `RestrictAddressFamilies=none`.
