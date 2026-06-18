# File Research: sources/virtualization/libguestfs/lib/inspect-osinfo.c

Purpose: Maps libguestfs inspection results to libosinfo-style OS IDs.

Key behavior:
- Reads inspected type, distro, major version, minor version, and for Windows sometimes product name, product variant, and build ID.
- Produces distro-specific IDs for CentOS, Circle, Rocky, Debian, Fedora, Mageia, SLES/SLE, Ubuntu, Arch, Gentoo, Void, ALT Linux, BSD variants, MS-DOS, and Windows.
- Windows 5.x/6.x maps to XP, 2003, Vista, 2008, 7, 2012, 8, 8.1, etc.
- Windows 10.0 server names distinguish 2016/2019/2022/2025 from product name.
- Windows client 10.0 uses build ID >= 22000 as Windows 11, otherwise Windows 10.
- Returns `"unknown"` when no ID can be inferred.

Dependencies and state:
- Depends on inspection getter APIs and `guestfs_int_parse_unsigned_int`.
- Stateless.

Risks:
- Mapping is heuristic and must track distro/libosinfo naming conventions.
- Windows Server detection relies on product name substrings.
