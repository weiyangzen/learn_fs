# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam_ppc.c

Parses PowerPC OpenFirmware device-tree iSCSI boot parameters from `/proc/device-tree`.

Main flow:
- Locates device tree root from `/chosen/bootpath` or related paths.
- Walks the tree to find iSCSI-capable NICs (`iscsi-toe` or `ethernet`) and `aliases/iscsi-disk` entries.
- Reads bootpath/property strings, parses them through the checked-in lexer/parser, and locates local MAC address files.
- Converts parsed OpenFirmware parameters into `boot_context`.

Parser callbacks:
- `obp_qual_set` records boot qualifiers such as bootp, dhcpv6, ipv6, iscsi, and ping.
- `obp_parm_addr`, `obp_parm_iqn`, `obp_parm_hexnum`, and `obp_parm_str` map textual parameter names to enum slots.
- Unknown parameters are printed but not fatal.

Exported functions:
- `fwparam_ppc_boot_info` fills one context for the boot target.
- `fwparam_ppc_get_targets` currently adds only the boot target to the list, with a comment noting it does not enumerate all possible targets.

Notable constraints:
- Static globals limit devices/NICs to `OFWDEV_MAX` of 10.
- NIC names are inferred as `ethN` by sorting discovered NIC paths.
