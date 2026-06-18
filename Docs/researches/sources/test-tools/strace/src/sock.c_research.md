# sources/test-tools/strace/src/sock.c

Purpose: decodes socket/network interface related ioctls, especially `ifreq` and `ifconf` payloads.

Important APIs/types/functions: `print_ifr_hwaddr`, `print_ifr_map`, `print_ifreq`, `print_ifc_len`, `print_ifconf_ifreq`, `decode_ifconf`, and `MPERS_PRINTER_DECL(sock_ioctl)`.

Control flow: ioctl switch handles `SIOCGIFCONF` with a two-phase decoder that saves the entry `ifconf`, then on exit prints returned length and either the buffer pointer or an array of `ifreq` entries. `ifreq` ioctls print input or output fields according to ioctl direction: socket addresses, hardware addresses, flags, indices, metrics, MTU, names, queue lengths, and maps. Unknown or broad legacy ioctls fall back to address-only printing.

State and persistence behavior: `decode_ifconf` stores the entry `ifconf` in tcb private data to compare returned length/buffer and print output arrays. Other paths are stateless stack fetches.

Dependencies and integration points: MPERS-aware `struct ifreq/ifconf`, socket address printer, hardware address helpers, `iffflags`, `arp_hardware_types`, and generic ioctl dispatcher.

Risks: `ifreq` union interpretation depends entirely on ioctl code. `ifconf` can change both length and pointer on exit, and array decoding depends on returned byte length being a multiple of `struct ifreq`.

Test signals: set/get address ioctls, flags, MTU, names, bridge add/delete, `SIOCGIFCONF` size-query and data-query modes, changed lengths, invalid pointers, and 32-bit personality layout.
