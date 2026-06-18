# sources/user-network-fs/samba/source3/nmbd/nmbd.c

## Purpose
`nmbd.c` is the main program and lifecycle manager for Samba's NetBIOS name service daemon. It initializes configuration, daemonization, messaging, WINS/name/browse state, sockets, subnets, signal handlers, async DNS, and then runs the nmbd periodic packet-processing loop.

## Important APIs, Types, and Functions
Global sockets are `ClientNMB`, `ClientDGRAM`, and `global_nmb_port`; `StartupTime` records daemon start. `nmbd_event_context()` returns the global tevent context. `terminate()` performs orderly shutdown by writing WINS data, releasing names, announcing removals, killing async DNS, unlinking pidfile, and exiting. Signal and stdin handlers route SIGTERM, SIGHUP, and foreground stdin EOF. `reload_interfaces()` reconciles interface additions/removals and waits for IPv4 non-loopback interfaces. `reload_nmbd_services()` and `msg_reload_nmbd_services()` reload smb.conf and refresh names/interfaces. `msg_nmbd_send_packet()` sends packets requested over Samba messaging. `process()` is the main loop. `open_sockets()` opens broadcast UDP sockets. `main()` wires all initialization steps.

## Control Flow
`main()` initializes talloc, command-line parsing, logging, signals, role checks, clustering, messaging, loadparm, NetBIOS names, daemon mode, optional async DNS, lock/pid directories, signal handlers, messaging handlers, sockets, interfaces, subnets, lmhosts, WINS, workgroup/name registration, packet server, daemon readiness, then calls `process()`. The main loop repeatedly checks elections, receives and processes packets, runs announcements, refreshes/flushes names and browse lists, handles WINS and browser synchronization, retransmits/expirs response records, checks child sync completion, syncs DMBs, and reloads interfaces.

## State and Persistence
State includes global sockets, global nmbd flags, workgroup/name/subnet structures, WINS database, browse list, pidfile, lock files, messaging registrations, and optional async DNS child. Persistent outputs include WINS database writes, browse list snapshots, pidfile, and logs.

## Dependencies and Integration Points
The file is the integration point for most nmbd subsystems declared in `nmbd.h` and `nmbd_proto.h`: packets, elections, WINS server/client, browse sync, interface management, lmhosts, messaging, server IDs, gencache, and Samba daemon utilities.

## Risks
The process loop is single-threaded and depends on cooperative periodic functions not blocking for long. Interface reload intentionally leaks removed subnet records rather than freeing possibly referenced memory. Only IPv4 non-loopback interfaces are handled for nmbd sockets. Shutdown order matters to avoid stale WINS registrations. AD DC role check prevents standalone nmbd, but can be inhibited by configuration.

## Test Signals
Tests should cover command-line options, daemon/foreground/stdin behavior, SIGTERM/SIGHUP and smbcontrol messages, AD DC role refusal, socket bind failures, interface add/remove/wait behavior, WINS init failures, registration failures, packet send validation, and main-loop periodic function scheduling.
