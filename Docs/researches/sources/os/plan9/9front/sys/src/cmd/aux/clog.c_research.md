# File Research: sources/os/plan9/9front/sys/src/cmd/aux/clog.c

Role: Console logger that timestamps lines read from a console device and appends them to a log file.

Main behavior:
- Opens the console path for reading and the log path for appending or creation with `DMAPPEND|0666`.
- Reads newline-delimited records with `Brdline`.
- Prefixes each complete line with a truncated `ctime(time(0))` timestamp and writes it to the log.
- If log writes fail, it closes, waits 500 ms, reopens, and retries.

Edge handling:
- On partial overlong lines, it discards buffered data with `Bread`.
- Exits on true EOF, read error, or unrecoverable console open failure.
