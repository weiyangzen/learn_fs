# File Research: sources/local-fs/e2fsprogs/misc/logsave.c

## Purpose
Implements `logsave`, running a command or copying stdin while saving output to a logfile that may not yet be writable.

## Key Elements
Parses `-a`, `-s`, and `-v`. Opens the target log for append or truncate; if opening fails, buffers output in memory. Writes a header with command/stdin and timestamp, then either forks/execs a child with stdout/stderr piped back or reads stdin directly.

`send_output` writes to console, log, or both, with skip-mode filtering so control-A/control-B bracketed text can appear on console but be omitted from the log. After command completion, writes a footer timestamp. If output was buffered because the log was unavailable, forks a background session that retries opening the log and writes buffered data later.

## Dependencies
Uses POSIX pipe/fork/execvp/waitpid, signal forwarding, read/write/open, and time APIs.

## Behavior/Risks
Buffers deferred log data entirely in memory. Background retry loops until the log can be opened. Signal handlers forward SIGINT/SIGTERM to the child. Output multiplexing is byte-stream based and intentionally simple for boot-time use.
