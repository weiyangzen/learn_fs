# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect-nbft.service.in

- Purpose: service started by network management after an NBFT interface is configured.
- Conditions/order: requires either ACPI NBFT table path, loads nvme-fabrics, waits for network-online, and runs before remote-fs-pre.
- Action: `@SBINDIR@/nvme connect-all --nbft`.
- Hardening: same style as other autoconnect units, with AF_INET/AF_INET6 address-family restriction.
