# File Research: sources/virtualization/spdk/app/vhost/vhost.c

This is a compact SPDK event-app launcher for the `vhost` application. The actual vhost functionality is provided by linked SPDK modules; this source handles app options, pidfile creation, socket path configuration, startup, and shutdown.

The custom options are `-f <path>` to save the process ID and `-S <path>` to set the vhost/vfio-user socket directory. `vhost_parse_arg()` stores the pidfile path or calls `spdk_vhost_set_socket_path()` and, when compiled with `SPDK_CONFIG_VFIO_USER`, `spdk_vfu_set_socket_path()`.

`save_pid()` writes the current PID to the configured path and exits on file creation failure. Unlike `spdk_tgt.c`, this file writes the pidfile before `spdk_app_start()`. The `vhost_started()` callback is empty, so all startup behavior comes from the SPDK app framework and linked modules.

`main()` initializes app opts with name `vhost`, parses SPDK common and custom arguments, writes the pidfile if requested, starts the app, finalizes with `spdk_app_fini()`, and returns the result. It exits immediately with the parser return code on argument failure.
