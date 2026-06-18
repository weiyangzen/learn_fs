# File Research: sources/virtualization/nvme-cli/libnvme/examples/mi-conf.c

This C example queries an NVMe-MI MCTP endpoint for optimal MTU and applies it locally through D-Bus and remotely through NVMe-MI config commands.

Core behavior:
- Parses endpoint strings of the form `mctp:<net>,<eid>`.
- Opens an MCTP endpoint with `libnvme_mi_open_mctp`.
- Finds an SMBus port by reading subsystem and port info.
- Reads current MCTP MTU via NVMe-MI.
- Sets device MCTP MTU through `libnvme_mi_mi_config_set_mctp_mtu`.
- Calls mctpd over system D-Bus to set local route MTU, adding 4 bytes for the MCTP header.
- Reverts device MTU if local D-Bus update fails and the old MTU was known.

Integration role:
- Demonstrates coordinated host route and device NVMe-MI MCTP MTU configuration.
- Depends on D-Bus and libnvme MI support.
