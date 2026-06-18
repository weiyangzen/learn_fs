# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifvlan.c

`ifvlan.c` implements VLAN configuration. It registers clone-time and runtime `vlan`, `vlandev`, and `vlanproto`, runtime `vlanpcp`, `-vlandev`, VLAN capability toggles, status reporting, and clone callbacks for `vlan` names and `parent.tag` names.

State is accumulated in static `struct vlanreq params`, using `NOTAG` and `NOPROTO` sentinels. `vlan_parse_ethervid()` derives parent and VLAN tag from interface names like `em0.100`, rejects invalid tags, and detects ambiguous command-line combinations.

`vlan_create()` validates that tag and parent are both supplied when either is present, defaults protocol to 802.1Q, and passes params to `ifcreate_ioctl()`. `vlan_cb()` enforces paired `vlan`/`vlandev` arguments for non-create workflows.

Runtime setters fetch existing VLAN config when possible, preserve missing counterpart fields, then call `SIOCSETVLAN`. `vlan_status()` prints tag, protocol, optional PCP, and parent interface.

Supported protocols are `802.1q`, `802.1ad`, and `qinq`, mapped to `ETHERTYPE_VLAN` and `ETHERTYPE_QINQ`. PCP is range checked to 0-7.

Notable behavior: VLAN tag parsing checks representability in `vlr_tag` after `strtoul()`, but relies on struct field truncation comparison rather than a named VLAN max constant.
