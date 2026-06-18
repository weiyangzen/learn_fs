# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmpd.c

Main `isakmpd` daemon entry point.

It parses command-line options for address families, acquire-only mode, config path, debug levels, FIFO/PID/report paths, packet capture, UDP/NAT-T ports, policy ignoring, passive shutdown mode, NAT-T disabling, and verbose logging. Startup sanitizes stdio, initializes logging, opens protocol/service databases, initializes the UI FIFO, daemonizes unless debugging, writes the PID file, starts privilege separation, initializes the unprivileged child, optionally starts IKE pcap logging, and enters the event loop.

The main loop handles SIGHUP reconfiguration, SIGUSR1 state reports, controlled shutdown, transport/UI/application readable fds, pending transport write fds, timer deadlines, message receiving/sending, UI/app handlers, and timer expirations. Shutdown queues DELETE notifications for phase-2 then phase-1 SAs unless disabled and exits only after prioritized send queues drain.

Notable behavior: `-S` disables SA deletion and makes the UI daemon passive; report generation temporarily redirects the current log channel to the report file opened through the monitor; the privileged parent never runs the normal event loop and instead enters `monitor_loop()`.
