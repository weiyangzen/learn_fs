# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-autoconnect.service.in

- Purpose: boot-time automatic NVMe-oF connect-all service.
- Conditions/order: runs when either `config.json` or `discovery.conf` exists, wants/after `modprobe@nvme_fabrics.service`, after network-online, before remote-fs-pre.
- Action: `@SBINDIR@/nvme connect-all --context=autoconnect`.
- Hardening: restricts filesystem, home, proc, kernel modules/logs/control groups, realtime, personality, IPC, W+X memory, and address families to IPv4/IPv6.
