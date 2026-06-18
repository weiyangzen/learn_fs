# sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool_netlink.h

Purpose: supplements the generated ethtool generic-netlink UAPI with manually maintained constants for flags, cable-test notifications, TDR payloads, and standardized Ethernet statistics groups.

Important APIs/types/functions: includes `ETHTOOL_FLAG_ALL`, cable result codes, cable pairs, cable information sources, cable test notification statuses, TDR amplitude/pulse/step/nest attribute enums, stats group IDs (`ETH_PHY`, `ETH_MAC`, `ETH_CTRL`, `RMON`, `PHY`), and detailed per-group statistic attribute IDs.

Control flow: no implementation. The implied netlink flow is a cable test or TDR action emitting started/completed notifications with nested result/fault/amplitude data, and stats requests returning nested standardized counters.

State and persistence behavior: cable-test/TDR values are transient diagnostic results; stats are live counters. The header does not define persistent configuration.

Dependencies: includes `<linux/ethtool.h>` for shared ethtool constants and `<linux/ethtool_netlink_generated.h>` for the generated family schema.

Integration points: strace decodes ethtool netlink notifications and stats attributes using these IDs in combination with the generated command/attribute tables.

Risks: this file and the generated header are coupled; mismatched bundled versions can decode command IDs but miss manual stat/cable nested IDs. The comments contain standard references that should not be collapsed into generic counter names.

Test signals: netlink decode tests should cover cable test started/completed notifications, TDR amplitude/pulse/step nesting, all stats group IDs, and at least one counter from each standardized stats group.
