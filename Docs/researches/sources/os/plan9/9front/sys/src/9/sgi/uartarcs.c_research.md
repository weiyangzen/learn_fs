# File Research: sources/os/plan9/9front/sys/src/9/sgi/uartarcs.c

Provides a Plan 9 UART abstraction over SGI ARCS firmware console calls. It creates a single `arcsuart`, uses ARCS service calls for polling input and output, and sets it as `consuart` during early console init.

`arcsproc` periodically polls firmware input and feeds characters into the UART layer. `kick` writes queued UART output through ARCS while holding `arcslock`. Most hardware-control callbacks are no-ops or validate only trivial settings: baud positive, bits 7/8, one stop bit, no parity.

This is an early/firmware console bridge, later disabled by graphics setup if Newport screen takes over.
