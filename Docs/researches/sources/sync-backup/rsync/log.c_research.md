# sources/sync-backup/rsync/log.c

## Purpose
`log.c` centralizes rsync diagnostics, daemon logging, transfer log formatting, deletion logging, stats snapshots, and exit-code reporting. It bridges local stdout/stderr output, multiplexed protocol messages, daemon log files, and syslog.

## Important APIs, Types, and Functions
Important public functions include `log_init()`, `logfile_close()`, `logfile_reopen()`, `rwrite()`, `rprintf()`, `rsyserr()`, `rflush()`, `remember_initial_stats()`, `log_format_has()`, `log_item()`, `maybe_log_item()`, `log_delete()`, and `log_exit()`. Internal helpers include `rerr_name()`, `logit()`, `syslog_init()`, `logfile_open()`, `filtered_fwrite()`, and `log_formatted()`. Global state includes `stats`, `got_xfer_error`, `output_needs_newline`, and `send_msgs_to_gen`.

## Control Flow
`log_init()` chooses a daemon log file or syslog and handles daemon restarts with changed module settings. `rwrite()` is the core dispatch path: it normalizes log codes, optionally forwards messages to the generator or remote peer, writes daemon logs with recursion protection, selects stdout or stderr, performs charset conversion if iconv is active, filters unsafe characters, and flushes line-ending messages. `rprintf()` and `rsyserr()` format safe bounded messages before calling `rwrite()`. `log_formatted()` expands `%` escapes in stdout and logfile formats using file metadata, stats deltas, daemon client identity, checksums, and itemized change flags.

## State and Persistence
Persistent effects are log-file appends, syslog writes, and protocol message sends. Process state tracks whether logging is initialized, whether the logfile was temporarily closed, initial byte counters for per-item deltas, and whether transfer errors occurred. `log_delete()` keeps a static synthetic `file_struct` for formatting deletion records.

## Dependencies and Integration Points
The file depends on rsync process-role globals, module config accessors (`lp_*()`), IO multiplexing (`send_msg()`), iconv wrappers, file metadata helpers, checksum formatting, and stats collected across sender, receiver, and generator. It is touched by most user-visible rsync operations.

## Risks
Logging runs in error paths, so recursion and buffer bounds are critical. The code includes explicit guards against non-NUL forwarded messages and cumulative `snprintf()` underflow. Format expansion can exit on oversized expansions. Message routing differs by daemon/server/client role and protocol version, so regressions can hide errors from users or break the wire protocol.

## Test Signals
Good tests cover daemon logfile fallback to syslog, logfile reopen after close, truncated long `rprintf()` output, `rsyserr()` bounds, non-printable filtering, UTF-8 and iconv error paths, server message forwarding for old protocol versions, `%i/%o/%f/%n/%L/%C` log format escapes, deletion logging, and `log_exit()` mappings for warning versus error exits.
