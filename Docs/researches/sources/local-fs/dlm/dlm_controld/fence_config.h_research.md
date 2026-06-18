# File Research: sources/local-fs/dlm/dlm_controld/fence_config.h

## Purpose
Public internal header for parsed fence configuration structures and helper functions.

## Main Contents
- Limits:
  - `FENCE_CONFIG_DEVS_MAX` = 4 devices per node.
  - `FENCE_CONFIG_NAME_MAX` = 256 bytes including NUL.
  - `FENCE_CONFIG_ARGS_MAX` = 4096 bytes including NUL.
- `struct fence_device`: device name, agent executable, device args, and unfence flag.
- `struct fence_connect`: connection name and per-node connection args.
- `struct fence_config`: arrays of device/connect pointers for one node plus nodeid and current position.
- Declares initialization, free, parallel/priority iteration, and final agent-argument construction functions.

## Integration Points
- Included by `dlm_daemon.h`.
- Implemented by `fence_config.c`, consumed by `fence.c` and `daemon_cpg.c`.

## Risks and Notes
- Structures expose raw pointers owned by `fence_config_init()`/`fence_config_free()`.
- Callers must respect `pos` and fixed array bounds.
