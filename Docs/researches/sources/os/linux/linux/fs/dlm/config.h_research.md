# File Research: sources/os/linux/linux/fs/dlm/config.h

## Role

Header for DLM configuration data, constants, and runtime configuration query APIs.

## Constants

- `DLM_MAX_SOCKET_BUFSIZE`: 4096.
- `DLM_MAX_ADDR_COUNT`: 8.
- Protocol identifiers:
  - `DLM_PROTO_TCP`
  - `DLM_PROTO_SCTP`

## Main Types

`struct dlm_config_node` describes a lockspace member returned to runtime code:

- `nodeid`
- `weight`
- `gone`
- `new`
- `comm_seq`
- `release_recover`

`struct dlm_config_info` stores global cluster configuration:

- TCP port.
- Buffer size.
- RSB table size.
- Recovery and scan timers.
- Logging toggles.
- Protocol.
- Socket mark.
- New RSB count.
- Recovery callback setting.
- Cluster name.

## Externs and APIs

Declares:

- `dlm_rhash_rsb_params`
- `dlm_config`
- `dlm_config_init()`
- `dlm_config_exit()`
- `dlm_config_nodes()`
- `dlm_comm_seq()`
- `dlm_our_nodeid()`
- `dlm_our_addr()`

## Research Notes

This header is the interface from the configfs-backed DLM configuration implementation to the rest of DLM. It exposes both static tunables and dynamic node/communication lookup helpers.
