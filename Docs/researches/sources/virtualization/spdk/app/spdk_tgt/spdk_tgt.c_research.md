# File Research: sources/virtualization/spdk/app/spdk_tgt/spdk_tgt.c

This is a small launcher for the general `spdk_tgt` application. It uses the SPDK event framework rather than implementing target behavior directly; the actual functionality comes from modules linked by the makefile and initialized through `spdk_app_start()`.

The file defines two app-specific options. `-f <file>` records a pidfile path in `g_pid_path`; `-S <path>` is compiled in when vhost or vfio-user support is enabled and sets the socket directory for both `spdk_vhost_set_socket_path()` and `spdk_vfu_set_socket_path()` as applicable. The option string is built with `SPDK_SOCK_PATH`, so `-S` is only accepted in builds with those features.

`spdk_tgt_save_pid()` writes the current process ID to the requested file and exits on failure. `spdk_tgt_started()` runs after the event application starts; it writes the pidfile if requested and dumps SPDK memory zones to stdout when the `MEMZONE_DUMP` environment variable is present. This is a diagnostic/startup hook rather than the main target loop.

`main()` initializes `spdk_app_opts`, sets `opts.name` to `spdk_tgt`, lets the SPDK app framework parse common and custom arguments, starts the app, finalizes it with `spdk_app_fini()`, and returns the app result code. The file is therefore a conventional SPDK event-app wrapper with pidfile and socket-path conveniences.
