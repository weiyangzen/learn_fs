# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/systemd/nvmf-connect@.service.in

- Purpose: templated service for discovery-controller event-driven NVMe-oF reconnect scans.
- Ordering: no default dependencies, after systemd-udevd, before local-fs-pre, part of and requiring `nvmf-connect.target`.
- Action: decodes escaped instance arguments into `CONNECT_ARGS` and runs `nvme connect-all --context=autoconnect --quiet ...`.
- Hardening: similar to autoconnect services, limited to IPv4/IPv6 address families.
