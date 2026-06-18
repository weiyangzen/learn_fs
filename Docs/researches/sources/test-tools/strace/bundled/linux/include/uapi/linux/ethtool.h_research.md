# sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool.h

Purpose: declares the legacy ioctl-based ethtool ABI and shared constants for link settings, driver info, wake-on-LAN, tunables, EEPROM/register access, coalescing, rings, channels, pause, EEE, strings/statistics, RX classification, RSS, firmware flashing/dumps, features, timestamping, per-queue ops, FEC, speeds, ports, wake flags, flow hash fields, module EEPROM IDs, reset flags, and link settings.

Important APIs/types/functions: major payload structs include `ethtool_cmd`, `ethtool_drvinfo`, `ethtool_wolinfo`, `ethtool_value`, `ethtool_tunable`, `ethtool_regs`, `ethtool_eeprom`, `ethtool_eee`, `ethtool_modinfo`, `ethtool_coalesce`, `ethtool_ringparam`, `ethtool_channels`, `ethtool_pauseparam`, string/stat/test structs, RX flow/classification structs, `ethtool_rxfh`, firmware/dump structs, feature block structs, `ethtool_ts_info`, `ethtool_per_queue_op`, `ethtool_fecparam`, and `ethtool_link_settings`. Command macros range from deprecated `ETHTOOL_GSET`/`SSET` through modern feature, channel, linksettings, PHY tunable, and FEC commands.

Control flow: no local implementation. Userspace normally passes an `ifreq` with an ethtool command struct pointer to `SIOCETHTOOL`; the first field is `cmd`, and the kernel interprets the remaining payload by command. Variable-length structs use trailing arrays sized by companion fields.

State and persistence behavior: exposes live NIC/PHY state, driver and firmware metadata, device settings, offload feature wishes/active states, RSS tables/keys, classification filters, module EEPROM pages, and firmware update/dump state. Some settings persist in device/driver configuration; many are runtime-only.

Dependencies: includes Linux networking, types, if_ether, and related UAPI dependencies earlier in the file. Shared constants are also consumed by ethtool netlink headers.

Integration points: strace decodes `SIOCETHTOOL` ioctl command IDs, nested payload structures, bitsets, speed/duplex/port/autoneg values, reset masks, flow specs, and feature/FEC flags. Modern netlink ethtool still reuses many constants from this header.

Risks: very large ABI surface with legacy and modern variants. Many structures are variable length; decoder bounds must honor `len`, `n_stats`, `rule_cnt`, `indir_size`, `hkey_size`, and feature block counts. Deprecated commands remain valid ABI names. Link mode bit indices grow over time, so old masks and `SUPPORTED_`/`ADVERTISED_` compatibility macros cover only legacy ranges.

Test signals: ioctl decode tests should include representative get/set commands, variable-length strings/stats/features, RX NFC rules, RSS contexts, link settings with high-speed modes, FEC masks, reset flags, module EEPROM, and unknown command fallback.
