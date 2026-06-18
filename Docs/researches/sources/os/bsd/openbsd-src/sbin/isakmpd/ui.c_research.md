# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ui.c

`ui.c` implements the legacy FIFO/stdin control interface for `isakmpd`. It creates `/var/run/isakmpd.fifo` unless `-f -` selects stdin, reads nonblocking commands line-by-line, and dispatches single-letter commands.

Supported command paths include connection setup (`c`), teardown (`t`/`T`), SA deletion by cookies/message ID (`d`), debug control (`D`), live config get/set/add/remove (`C`), packet logging (`p`), shutdown (`Q`), reload/reinit (`R`), report output (`r`/`S`), and active/passive mode switching (`M`). Configuration changes to phase-2 connection lists schedule a delayed connection reinitialization timer.

Results that need file output are written through `monitor_fopen()` to `/var/run/isakmpd.result`. The command parser uses bounded `sscanf()` fields and hex decoding for SA cookies, but it is a trusted local-control interface with broad daemon control authority.

Notable coupling: calls into connection, SA, exchange, timer, config, logging, monitor, and daemon shutdown/reinit code.
