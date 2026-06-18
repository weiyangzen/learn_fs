# File Research: sources/os/bsd/openbsd-src/sbin/iked/iked.c

`iked.c` is the daemon entry point and parent-process coordinator. It parses command-line options, initializes global daemon state, starts privsep children, configures logging/signals, loads configuration, passes privileged resources to children, and handles reload/shutdown.

The privsep layout contains CA, control, and IKEv2 children. Startup parses config, opens PF_KEY and UDP sockets, reads/sends key material to CA, resets CA state, compiles policies in IKEv2, configures static daemon settings, coupling, OCSP, RADIUS, and finally active/passive mode.

The parent process handles SIGHUP reloads, SIGTERM/SIGINT shutdown, child death, and control-plane messages. Reload either resets/reloads policies/RADIUS/CA and reparses config, or forwards targeted reset modes to IKEv2 and CA. Parent dispatch also handles OCSP socket connection and virtual route/address/DNS requests from IKEv2.

Security-relevant details: root is required unless no-action mode is selected, pledge is applied after privileged setup, process titles/instances are controlled through privsep options, and shutdown kills children before cleaning virtual routes and freeing parent state.
