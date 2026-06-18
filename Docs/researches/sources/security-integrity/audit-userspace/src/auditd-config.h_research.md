# sources/security-integrity/audit-userspace/src/auditd-config.h

## Purpose
`auditd-config.h` defines the central audit daemon configuration contract. Its `struct daemon_conf` is the shared state object loaded from configuration and consumed by daemon startup, event logging, network listening, dispatcher setup, and live reconfiguration.

## Important APIs, Types, And Functions
The header declares `CONFIG_FILE`, `MEGABYTE`, `EOE_TIMEOUT`, daemon/log/flush/action/node/overflow/transport enums, `struct daemon_conf`, and configuration functions from `auditd-config.c`. It conditionally exposes `start_config_manager` only after `AUDITD_EVENT_H` is visible, reflecting the circular relationship between config loading and reconfigure events.

## Control Flow
The header itself has no runtime flow, but it encodes the shape of flow between modules. `load_config` fills the struct, `resolve_node` materializes node naming after startup, `setup_percentages` converts percent thresholds once a log fd exists, and `free_config` tears down string ownership. Daemon code passes the same struct pointer through initialization and later reconfiguration.

## State And Persistence
Persistent settings represented here include log path/format/group, rotation limits, disk threshold actions and helper paths, mail recipient and verification flag, TCP/GSS listener settings, dispatcher queue/restart controls, plugin directory, custom config directory, and user-space end-of-event timeout. Several fields are owned heap strings and require disciplined transfer/free behavior.

## Dependencies And Integration
The header depends on `libaudit.h`, `gcc-attributes.h`, and `<grp.h>`. It is included by auditd core, event, listener, dispatcher, and reconfigure modules, making it the ABI-like internal contract for audit daemon behavior.

## Risks
The main risk is ownership ambiguity: many fields are `const char *` but point to heap allocations that are freed or transferred during reconfiguration. Enum ordering is also externally meaningful inside string lookup tables such as `failure_actions`.

## Test Signals
Tests that instantiate `daemon_conf` should verify defaults from `clear_config`, string cleanup from `free_config`, and live reconfiguration ownership transfer. Compile tests should cover both listener/GSS enabled and disabled builds because this header shapes both configurations.
