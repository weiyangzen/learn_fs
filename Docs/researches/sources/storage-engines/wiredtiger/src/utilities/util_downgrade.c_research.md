## sources/storage-engines/wiredtiger/src/utilities/util_downgrade.c

Purpose: implements `wt downgrade`, reconfiguring a database's compatibility release through the connection API.

Important APIs/types/functions: `util_downgrade` requires `-V release`, formats `compatibility=(release=%s)` into a fixed buffer, obtains `session->connection`, and calls `conn->reconfigure(conn, config_str)`. Usage documents `downgrade -V release`.

Control flow: parse only `-V` and `-?`, reject extra positional arguments or missing release, build the compatibility config string, reconfigure the connection, and return `0` or `util_err` output.

State and persistence behavior: changes persistent compatibility metadata and can influence log/file removal and future open compatibility. It does not itself force checkpoints or close/reopen; `util_main.c` closes the connection after the command, allowing WiredTiger close processing to persist required state.

Dependencies and integration points: depends on `WT_CONNECTION.reconfigure` compatibility handling and the open connection/session from `util_main.c`. It interacts indirectly with recovery/log code that honors downgrade flags and forced log removal.

Risks: fixed 128-byte buffer assumes release strings are short; oversized strings fail via `__wt_snprintf`. The release string is not sanitized by the wrapper and relies on config validation. Downgrade is a high-impact operation that can restrict future access by newer features.

Test signals: valid release downgrade, missing/extra argument usage, invalid release rejection, close/reopen with downgraded compatibility, and log removal behavior when newer log files exist.
