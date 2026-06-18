# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcoe/fcoeio.h

## Role

`fcoeio.h` defines the user/kernel ioctl ABI for managing FCoE ports.

## Ioctl Envelope

- Defines top-level ioctl command `FCOEIO_CMD` and sub-command base `FCOEIO_SUB_CMD`.
- Subcommands create a port, delete a port, and get the FCoE port list.
- Defines transfer direction flags `FCOEIO_XFER_NONE`, `FCOEIO_XFER_READ`, `FCOEIO_XFER_WRITE`, and `FCOEIO_XFER_RW`.
- Defines `fcoeio_stat_t` error/status values for invalid argument, busy, already exists, PWWN/NWWN conflicts, MAC create/open failures, port creation failure, jumbo-frame requirement, MAC not found, offline failure, and more-data.
- `fcoeio_t` is the ioctl envelope with transfer direction, command, flags, command flags, input/output/aux lengths, status, and 64-bit user buffer addresses.

## Port Payloads

- Defines client port types `FCOE_CLIENT_INITIATOR` and `FCOE_CLIENT_TARGET`.
- `fcoeio_create_port_param_t` carries port/node WWNs, provided flags, force-promiscuous flag, port type, and datalink id.
- `fcoeio_delete_port_param_t` carries datalink id.
- `fcoe_port_instance_t` reports port WWN, datalink id, factory/current MACs, promiscuous state, port type, and MTU.
- `fcoe_port_list_t` is a variable-length list headed by `numPorts`.
