# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/65-persistent-net-nbft.rules.in

- Purpose: udev rule to preserve NBFT network interface names.
- Behavior: for non-remove net events where `INTERFACE` matches `nbft*`, assigns the kernel name from the interface environment value.
