# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunos_dhcp_class.h

`sunos_dhcp_class.h` defines SunOS/Solaris vendor-class DHCP option numbers used by DHCP clients/tools and network boot paths. `VS_OFFSET` is 256 for `dhcpinfo` option numbering.

Vendor-specific options cover NFS root mount options, root server IP/name, root path, swap server and swap file, boot file, POSIX timezone, boot NFS read size, install server IP/name/path, sysid and JumpStart server paths, terminal type, network boot standalone URI, and WAN boot HTTP proxy. `VS_OPTION_END` is kept equal to the highest defined option.

The file is pure constants and has no kernel-only section.
