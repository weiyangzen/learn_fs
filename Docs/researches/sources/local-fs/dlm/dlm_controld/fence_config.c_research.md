# File Research: sources/local-fs/dlm/dlm_controld/fence_config.c

## Purpose
Parses DLM fence configuration from `dlm.conf`-style sections and provides iteration and argument construction helpers for fencing/unfencing.

## Main Behavior
- Supports two config forms:
  - `fence_all <name> <agent> <args>` plus optional `unfence_all`, applying one device to all nodes.
  - Repeated `device <name> <agent> <args>` sections with `connect <name> node=<nodeid> <args>` and optional `unfence <name>`.
- `fence_config_init()` scans the config file for devices connected to a target node and fills up to `FENCE_CONFIG_DEVS_MAX` device/connect pairs.
- `read_config_section()` validates device/connect name matching, finds the target node's connection line, captures device and connection args, and tracks unfence markers.
- `same_base_name()` treats device names with matching prefixes before `:` as parallel devices.
- `fence_config_next_parallel()` advances to the next device with the same base name.
- `fence_config_next_priority()` advances to the next device with a different base name.
- `fence_config_agent_args()` combines device args, connection args, optional extra args, converts spaces to newlines, and adds `node=<nodeid>` when missing.
- `fence_config_free()` releases allocated device/connect entries and zeroes the config.

## Integration Points
- Public declarations are in `fence_config.h`.
- Used by `fence.c` and `daemon_cpg.c`.
- Falls back to a global `fence_all_device` in `daemon_cpg.c` when no node-specific config exists.

## Risks and Notes
- Config grammar is line-oriented and intentionally narrow; malformed sections return negative errno-style errors.
- `fence_config_init()` increments `pos` without an explicit bound check before assigning arrays, so configs listing more than four devices for a node can overflow the fixed arrays.
- Argument conversion is simplistic: every space becomes newline, so values containing spaces are not representable.
