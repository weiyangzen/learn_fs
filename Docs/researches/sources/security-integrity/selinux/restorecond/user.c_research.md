# sources/security-integrity/selinux/restorecond/user.c
# sources/security-integrity/selinux/restorecond/user.c

Purpose: user-session restorecond server implementation using GLib main loop, optional session DBus name ownership, and local lock fallback.

Important APIs and control flow: under `HAVE_DBUS`, `start()` pings `org.selinux.Restorecond` on the session bus to trigger activation, and `dbus_server()` owns that bus name. Without DBus ownership, `local_server()` takes `~/.restorecond` with `flock()` and watches stdin for terminal/session disappearance. `server()` creates a `GMainLoop`, chooses DBus or local mode, reads config, exits if watch list is empty, sets matchpathcon flags, wraps the inotify fd in a nonblocking `GIOChannel`, handles inotify events in `io_channel_callback()`, handles stdin in `stdin_callback()`, and quits on SIGTERM.

State and persistence: local lock file in the user's home, inotify watch state from `watch.c`, GLib event sources, and DBus name ownership. Relabeling persists through `watch_list_find()`.

Dependencies and integration points: depends on GLib, optionally GIO/DBus, libselinux, `watch.c`, and `restorecond_user.service`.

Risks and test signals: DBus failure falls back to local lock, but systemd user unit with `Type=dbus` may not consider fallback successful. Several callbacks call `exit(0)` directly, relying on process teardown. No direct tests cover DBus/local modes.
