## sources/user-network-fs/nfs-utils/utils/statd/statd.c

Purpose: Main daemon for Linux NSM `rpc.statd`, handling configuration, daemonization, RPC listener setup, notification startup, state loading, privilege dropping, and service loop execution.

Important APIs/types/functions: Defines globals `run_mode`, `ha_callout_prog`, `SM_stat_chge`, ports, and option table. Key functions include `statd_unregister`, signal handlers, `create_pidfile`, `truncate_pidfile`, `run_sm_notify`, `set_nlm_port`, `read_statd_conf`, and `main`.

Control flow: Startup reads config/env, parses options, rejects duplicate statd, validates ports, optionally delegates notify-only mode to `sm-notify`, limits file descriptors, sets lockd ports via procfs, daemonizes, registers signals, writes pid file, runs `sm-notify` unless disabled, creates reserved callback socket, loads persistent monitor state, obtains NSM state, unregisters stale RPC registrations, drops privileges, creates RPC listeners, announces readiness, then repeatedly runs `my_svc_run`.

State and persistence: Uses `/run/rpc.statd.pid`, NSM state directory, kernel NSM state, `/proc/sys/fs/nfs/nlm_*port`, and rpcbind registrations. Runtime globals control modes and local name/state.

Dependencies and integration: Integrates with config file, `support/nsm`, nfs-utils daemon helpers, libtirpc RPC service creation, tcp_wrappers when enabled, lockd procfs controls, and `sm-notify`.

Risks and test signals: Startup ordering is security-sensitive: reserved socket before privilege drop, unregister before listener creation, and pid handling. Tests should cover config/CLI precedence, duplicate daemon detection, no-notify env, port validation, privilege drop failure, listener creation failure, signal cleanup, and `sm-notify` fork path.
