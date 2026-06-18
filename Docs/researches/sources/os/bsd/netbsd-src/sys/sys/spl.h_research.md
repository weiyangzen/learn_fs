# File Research: sources/os/bsd/netbsd-src/sys/sys/spl.h

Read completely: 63 lines.

This kernel/KMEMUSER-only header is intended for machine-dependent headers. It generates inline `spl*` interrupt-priority raisers from IPL constants using `splraiseipl(makeiplcookie(IPL_*))`.

It conditionally emits soft interrupt variants for available IPLs and always emits `splvm`, `splsched`, and `splhigh`.

Risks: it assumes `makeiplcookie` is reasonably fast and that machine-dependent IPL names exist. Ports with slow generic IPL construction should provide optimized MD functions instead.
