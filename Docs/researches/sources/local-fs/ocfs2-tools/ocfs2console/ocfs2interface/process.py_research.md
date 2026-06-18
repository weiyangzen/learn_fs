# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/process.py

Subprocess wrapper with GTK progress dialog and output capture.

Key class:
- `Process`
  - Starts command immediately using `popen2.Popen4`.
  - `reap()`:
    - Sets child stdout/stderr nonblocking.
    - Adds GLib timeout polling.
    - Adds IO watch for output.
    - Runs nested `gtk.main()` until process exits or is killed.
    - Destroys progress dialog and removes watches.
    - Returns `(success, output, killed)`.
  - `timeout()`:
    - Polls process.
    - Sets success from exit status.
    - Kills after timeout.
    - Pulses progress dialog if visible.
  - `kill()`:
    - Sends SIGTERM, schedules SIGKILL fallback.
  - `make_progress_box()`:
    - Builds modal progress window.
  - `read()`:
    - Appends child output.

Constants:
- `INTERVAL = 100`
- `TIMEOUT = 10000`

Notable details:
- If `command` is a string with multiple words, `popen2.Popen4` invokes shell-style command handling.
- `threshold = self.count - INTERVAL * 10` makes delayed progress threshold negative with current constants, so non-`spin_now` operations may never show progress before timeout.
- Uses nested GTK main loop for synchronous command behavior.
