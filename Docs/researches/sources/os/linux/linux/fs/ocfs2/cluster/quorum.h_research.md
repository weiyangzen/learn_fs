# File Research: sources/os/linux/linux/fs/ocfs2/cluster/quorum.h

Header for OCFS2 quorum logic.

Declares:
- Lifecycle: `o2quo_init()`, `o2quo_exit()`.
- Heartbeat events: `o2quo_hb_up()`, `o2quo_hb_down()`, `o2quo_hb_still_up()`.
- Network events: `o2quo_conn_up()`, `o2quo_conn_err()`.
- Disk timeout fencing entry: `o2quo_disk_timeout()`.

Role:
- Used by heartbeat and network transport code to coordinate self-fencing decisions.
