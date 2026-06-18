# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/nm-dispatcher/80-nvmf-connect-nbft.sh.in

- Purpose: NetworkManager dispatcher script for NBFT-defined NVMe-oF connections.
- Trigger logic: on interface `up`, starts NBFT reconnect when interface name begins with `nbft` or `CONNECTION_ID` begins with `NBFT connection HFI`.
- Action: starts `nvmf-connect-nbft.service` asynchronously with substituted `@SYSTEMCTL@`; failures are ignored.
