# File Research: sources/virtualization/nbdkit/filters/log/log.h

Shared declarations for the log filter. Defines `log_id_t`, per-connection `struct handle`, and global logging state such as connection count, logfile, script, append mode, and mutex.

Provides `get_id()` for per-connection transaction IDs under the global lock. Declares `enter()`, `leave()`, `print()`, and `leave_simple()` helpers implemented in `output.c`.

Defines the `LOG` macro, which uses GCC cleanup attributes to automatically emit a matching leave record on every exit path from simple callbacks.
