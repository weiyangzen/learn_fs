# File Research: sources/os/linux/linux-stable/fs/dlm/config.h

## Purpose

Defines the public internal DLM configuration types, constants, global configuration object, and accessor prototypes used outside `config.c`.

## Main Responsibilities

- Defines `DLM_MAX_SOCKET_BUFSIZE`, `DLM_MAX_ADDR_COUNT`, and protocol constants for TCP/SCTP.
- Defines `struct dlm_config_node`, the membership snapshot returned to DLM code.
- Declares DLM resource rhashtable parameters.
- Defines `struct dlm_config_info`, the global cluster/runtime configuration structure.
- Declares `dlm_config_init()`, `dlm_config_exit()`, `dlm_config_nodes()`, `dlm_comm_seq()`, `dlm_our_nodeid()`, and `dlm_our_addr()`.

## Important Fields

`struct dlm_config_info` includes:
- TCP port and protocol.
- Buffer and resource table sizing.
- Recovery, toss, and scan timers.
- Debug/info logging toggles.
- Network packet mark.
- New resource count and recovery callback settings.
- Cluster name.

## Dependencies

- DLM lockspace length constants.
- Linux socket address storage for local address access.
- Used by DLM communications, membership, lockspace, and recovery code.
