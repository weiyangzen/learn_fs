# File Research: sources/local-fs/dlm/dlm_controld/node_config.h

This header declares the per-node configuration interface.

It defines:
- `struct node_config { uint32_t mark; }`
- `node_config_init(const char *path)`
- `node_config_get(int nodeid)`

The comments define return semantics for configuration lookup/parsing:
- `-ENOENT` means the path or node config is absent.
- Other negative errors indicate config problems.
- `0` means config was found with no problems.

The implementation in `node_config.c` currently treats a missing file as non-fatal default configuration and returns `0`.
