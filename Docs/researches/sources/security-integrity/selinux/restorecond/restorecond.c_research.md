# sources/security-integrity/selinux/restorecond/restorecond.c
# sources/security-integrity/selinux/restorecond/restorecond.c

Purpose: main daemon entrypoint for monitoring configured paths and restoring default SELinux file contexts when watched files appear or change.

Important APIs and control flow: defines global daemon state (`homedir`, `master_fd`, `r_opts`, `debug_mode`, `terminate`, `master_wd`, `run_as_user`, `foreground_mode`). `main()` exits if SELinux is disabled, initializes restore options with ignore-noentry/digest/skip-multilink flags, installs SIGTERM handling, parses `-d`, `-f`, `-F`, `-u`, `-v`, opens inotify, determines home directory, and selects root daemon vs user path. Non-root runs try `start()` DBus activation, falling back to local `server()`. Root reads config, daemonizes unless debug/foreground, writes `/run/restorecond.pid`, and loops in `watch()`. `done()` frees watch state, closes inotify, frees utmp watcher, and closes selabel handle.

State and persistence: maintains inotify descriptors, a pidfile, global restore options, watch lists in `watch.c`, and utmp state. It performs persistent file relabeling through `selinux_restorecon()`.

Dependencies and integration points: integrates `restore.c`, `watch.c`, `user.c`, `utmpwatcher.c`, systemd unit files, config files, and libselinux.

Risks and test signals: global state is shared across modules. Signal handler closes `master_fd` to break reads, which depends on watch-loop behavior. Startup hard-exits on config/watch failures. No dedicated tests are present.
