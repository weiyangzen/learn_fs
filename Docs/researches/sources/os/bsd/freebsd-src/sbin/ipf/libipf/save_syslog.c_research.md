# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_syslog.c

`ipmon` syslog saver backend.

Key behavior:
- Registers `syslogsaver`.
- Parses optional `facility.priority`, `.priority`, or `facility.` override.
- Sends messages to `syslog()` using either configured facility/priority or the message log level.

Research notes:
- Invalid facility or priority names reject parser setup.
