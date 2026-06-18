# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_config.h

Private configuration header for `libisns`.

Defines debug macro `DBG`, includes internal modules, defines mutex type constants, and declares `struct isns_config_s`.

The config structure tracks:
- kqueue and control pipe descriptors
- control thread pointer
- socket state and address info
- current input PDU
- task queue mutex/current task/queue head
- transaction mutex
- server/client mode flag
- registration refresh state

Also provides `isns_is_socket_init_done`.
