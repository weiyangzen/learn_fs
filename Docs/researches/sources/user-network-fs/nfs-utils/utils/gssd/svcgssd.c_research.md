# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd.c

Purpose: `svcgssd.c` is the main program for the server-side RPCSEC_GSS daemon. It initializes configuration, logging, GSS credentials, libevent, NFSv4 idmapping, and a procfs channel reader for `/proc/net/rpc/auth.rpcsec.init/channel`.

Important APIs and functions: `main()` parses `-f`, `-i`, `-v`, `-r`, `-n`, and `-p`, reads `svcgssd` settings from `NFS_CONFFILE`, calls `gssd_check_mechs()`, `gssd_acquire_cred()`, `nfs4_init_name_mapping()`, and dispatches libevent. `svcgssd_nullrpc_cb()` reads a kernel null-init request and passes it to `handle_nullreq()`. `svcgssd_nullrpc_open()`, `svcgssd_nullrpc_close()`, and `svcgssd_wait_cb()` manage delayed availability of the kernel proc channel. `sig_die()` and `sig_hup()` implement shutdown and ignored reload behavior.

Control flow: startup reads config, applies debug levels, daemonizes, acquires either machine credentials, a configured principal, or nameless credentials, then opens or waits for the nullrpc channel. Once libevent is running, readable channel data is converted from newline-terminated kernel text into a mutable string for `svcgssd_proc.c`.

State and persistence: process-global state tracks signal receipt, event base, channel fd, and event handles. Persistent external state is in kernel procfs RPCSEC_GSS caches plus Kerberos credentials acquired by gssd helpers. Shutdown frees events, name mapping, enctype caches, and GSS state.

Dependencies and integration: integrates with libevent, libtirpc/authgss debug APIs, libnfsidmap, nfs-utils config/logging helpers, GSSAPI, and kernel `/proc/net/rpc/auth.rpcsec.init/channel`.

Risks: procfs channel failures leave the daemon waiting; double signal forces exit; credential acquisition failures are fatal. Test signals include option parsing, config precedence, missing channel wait/reopen, signal-triggered event-loop exit, foreground/background daemon readiness, and credential acquisition paths for `-n`, `-p`, and default hostbased `nfs`.
