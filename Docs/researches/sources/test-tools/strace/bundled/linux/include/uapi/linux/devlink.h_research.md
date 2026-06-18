# sources/test-tools/strace/bundled/linux/include/uapi/linux/devlink.h

Purpose: defines the devlink generic netlink ABI for managing and observing physical/network devices, ports, shared buffers, eswitches, resources, regions, health reporters, flash updates, traps, rates, linecards, selftests, and function capabilities.

Important APIs/types/functions: exported constants include `DEVLINK_GENL_NAME`, version, multicast group names, and index bus name. `enum devlink_command` is the command ABI. Supporting enums cover port type/flavour/function state, shared-buffer pool/threshold types, eswitch modes, rate types, parameter config modes, firmware-load/reset policies, flash overwrite bit masks, selftest IDs/results, trap action/type, reload action/limit, linecard state, variable attr types, dpipe fields, resources, and port-function caps. `enum devlink_attr` is the large typed attribute namespace with explicit comments for payload type.

Control flow: no implementation is present. The implied flow is generic-netlink command dispatch with nested attributes, dumps for get commands, notifications for new/del/status events, and command-specific validation in the kernel.

State and persistence behavior: devlink exposes live driver/device state plus persistent-ish firmware/device configuration such as parameters, flash components, resources, and port functions. Reload, health, and flash status attributes model long-running state transitions, while traps/statistics are runtime counters and policies.

Dependencies: includes `<linux/const.h>` for `_BITUL` masks. Generic netlink types and nested attribute parsing are external.

Integration points: strace decodes devlink netlink commands/attributes and bitfields. The header is coordinated with kernel devlink YAML/spec generation comments for newer attributes and with network drivers that expose devlink instances.

Risks: command and attribute order is explicitly ABI; inserting values in the middle breaks decoders. Obsolete eswitch command aliases intentionally map to current IDs. Attribute comments are the main local type metadata, so stale comments can cause wrong pretty-printers. Future YAML-generated changes must keep `DEVLINK_ATTR_MAX` and masks aligned.

Test signals: decoder tests should cover representative GET dump commands, port function capability bitfields, reload action/limit masks, flash overwrite masks, trap policer attrs, health reporter attrs, linecard attrs, and unknown attributes beyond `DEVLINK_ATTR_MAX`.
