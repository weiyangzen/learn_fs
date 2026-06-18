# File Research: sources/os/linux/linux-stable/fs/smb/server/proc.c

This file implements `/proc/fs/ksmbd` reporting and percpu counters for ksmbd when proc support is built.

Global state:
- `ksmbd_proc_fs`: root proc directory entry.
- `ksmbd_counters`: global ksmbd percpu counters.

Functions:
- `ksmbd_proc_create()`
  - Creates a read-only single-data proc file under `/proc/fs/ksmbd`.

- `proc_show_ksmbd_stats()`
  - Emits server metadata:
    - server string
    - NetBIOS name
    - workgroup
    - min/max protocol
    - flags
    - fake filesystem capabilities
    - session count
    - tree connect count
    - read bytes
    - written bytes
  - Emits SMB2 command counters for all request slots from negotiate through oplock break.

- `ksmbd_proc_cleanup()`
  - Removes proc tree and destroys all percpu counters.
  - Sets `ksmbd_proc_fs` to NULL.

- `ksmbd_proc_reset()`
  - Resets all counters to zero.

- `ksmbd_proc_init()`
  - Creates `/proc/fs/ksmbd`.
  - Creates `sessions` directory.
  - Initializes all percpu counters.
  - Creates `server` proc file.
  - Resets counters.
  - Cleans up on partial failure.

Data tables:
- `smb2_process_req[]`
  - Maps SMB2 command constants to human-readable names for proc output.

Dependencies:
- `server_conf` and server string accessors from `server.c`.
- Protocol-name helper `ksmbd_get_protocol_string()`.
- Counter helpers from `stats.h`.

Risk areas:
- Counter initialization and cleanup are coupled to proc directory creation; partial initialization failure uses `ksmbd_proc_cleanup()`.
- The command-name table size is `KSMBD_COUNTER_MAX_REQS`; it must stay aligned with counter indices and SMB2 command ordering.
