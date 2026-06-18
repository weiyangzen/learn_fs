# sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool_netlink_generated.h

Purpose: auto-generated UAPI schema for the ethtool generic netlink family, generated from `Documentation/netlink/specs/ethtool.yaml`.

Important APIs/types/functions: defines `ETHTOOL_GENL_NAME`, version, UDP tunnel types, common header flags, TCP data split values, hardware timestamp source, PSE event bits, common header/bitset/string/string-set attributes, and per-operation attribute namespaces for rings, MM, linkinfo, linkmodes, linkstate, debug, WOL, features, channels, IRQ moderation/profile, coalesce, pause, EEE, timestamp info/config, cable tests, tunnel info, FEC, module EEPROM/module power, stats, PHC vclocks, PSE, RSS, PLCA, module firmware flash, PHY, MSE, plus user and kernel message enums and monitor multicast group.

Control flow: no executable implementation. The generated enums define generic-netlink request, reply, action, notification, and nested attribute IDs. The user message enum drives userspace requests/actions; kernel message enum drives replies and notifications.

State and persistence behavior: models live ethtool netlink state and configuration for NIC/PHY properties. Some operations mutate driver/device settings, while notifications report asynchronous changes such as link mode, rings, channels, pause, EEE, FEC, module, PSE, PLCA, MM, PHY, RSS, and firmware flash progress.

Dependencies: generated as a standalone UAPI header but included by `ethtool_netlink.h`. It must stay synchronized with kernel YAML specs and ethtool core implementation.

Integration points: strace uses it as the authoritative source for ethtool netlink message and attribute names. Network tooling uses the same IDs for modern ethtool operations instead of `SIOCETHTOOL`.

Risks: generated order is ABI; manual edits are forbidden by the header. Many namespaces begin at zero, but some begin at one for padding/reserved conventions, so decoders must not normalize them. User and kernel message enums are related but not identical; set replies and notifications have separate IDs.

Test signals: decode tests should cover at least one request/reply pair, one notification, common header flags, nested bitsets/strings, RSS create/delete actions, module firmware flash notifications, PSE events, timestamp config, MSE attributes, and unknown future attributes beyond each `*_MAX`.
