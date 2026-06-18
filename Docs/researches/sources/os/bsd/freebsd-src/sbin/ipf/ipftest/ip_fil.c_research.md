# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/ip_fil.c

`ip_fil.c` supplies user-space kernel compatibility hooks for `ipftest`. It lets kernel IPFilter modules run in a test harness without real kernel networking.

Major behaviors:
- Defines the global `ipfmain` softc.
- Provides trivial `ipfattach()`/`ipfdetach()`.
- Routes ioctl handling through `ipf_ioctlswitch()` with the current UID.
- Maintains synthetic `ifnet` objects in an expandable array, parses names with optional `=address`, initializes address lists, and resolves interface names.
- Provides fake interface output functions: `no_output()` discards packets, while `write_output()` appends packet bytes to `/tmp/<ifname>` for saved outbound traffic.
- Implements `ipf_fastroute()` by selecting a destination/interface, running accounting/state/NAT checkout, printing the packet, and calling the synthetic interface output callback.
- Provides test versions of reset/ICMP error sending, mbuf free/copy, uio read movement, interface address lookup, source verification, packet injection, pullup, pseudo checksums, pseudo random values, and IP ID/ISS generation.

Notable details:
- `ipf_newisn()` uses the bundled MD5 implementation over flow tuple data plus a monotonic offset, with the secret update commented out.
- `ipf_random()` deliberately returns boundary-case values for early calls to exercise test ranges.
- `ipf_pullup()` intentionally fails when the requested length exceeds current mbuf length, setting `FRB_PULLUP`.
- There is a suspicious syntax fragment in `ipf_fastroute()` as read: `return (0; /* no routing table out here */);`, which looks malformed unless hidden by build conditions or historical source context.
