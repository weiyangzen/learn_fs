# File Research: sources/virtualization/nbdkit/filters/log/output.c

Implements output backends for the log filter. `to_file()` writes timestamped log entries to the configured FILE, using `flockfile()` when available and flushing each line.

`to_script()` builds shell variable assignments and message content in an `open_memstream()`, appends the configured script body, executes it with `system()`, and logs but ignores script exit status.

`enter()`, `leave()`, and `print()` dispatch each event to file and/or script. `leave_simple()` maps nbdkit-visible errno values into canonical protocol error names such as `EPERM`, `EIO`, `ENOMEM`, `ENOSPC`, `ENOTSUP`, and `EOVERFLOW`.

`leave_simple2()` is the cleanup callback used by the `LOG` macro.
