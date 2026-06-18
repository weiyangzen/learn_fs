# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/70-nvmf-keys.rules.in

- Purpose: loads NVMe/TCP TLS pre-shared keys when kernel support appears.
- Trigger: module add event for `nvme_tcp` when `@SYSCONFDIR@/nvme/tls-keys` exists.
- Action: runs `nvme tls --import --keyfile @SYSCONFDIR@/nvme/tls-keys`.
