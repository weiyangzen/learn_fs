# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sdlpi.c

This is the STREAMS/DLPI output backend for `ipsend`, used for Solaris/HP-UX style systems.

`initdevice()` constructs a `/dev/<interface-base>` device path, extracts the numeric PPA from the interface name, opens the DLPI provider, attaches to the PPA, binds to IP SAP or HP raw mode, optionally enables promiscuous SAP, and requests raw DLPI mode when `DLIOCRAW` exists.

`sendip()` sends a frame using `putmsg()`, optionally with HP rawdata control, then flushes the write queue.

Important dependencies include DLPI headers, STREAMS headers, `dlcommon.c` helper routines, and `ipsend.h`.

Implementation notes and risks:
- Device name parsing assumes interface names end in digits.
- Error paths frequently call `exit()`.
- The backend is legacy platform-specific code.
