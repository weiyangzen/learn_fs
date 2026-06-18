# File Research: sources/os/bsd/freebsd-src/sbin/dump/unctime.c

Provides `unctime()`, a small parser converting `ctime(3)`-style strings into `time_t`.

Behavior:
- Uses `strptime(str, "%a %b %e %T %Y", &then)`.
- Accepts strings ending immediately or at a newline.
- Sets `tm_isdst = -1` before `mktime()` so libc determines DST.
- Returns `(time_t)-1` on parse failure.

Usage:
- Used by dumpdates parsing in `itime.c`.
- Used by `main.c` for the `-T date` option.

Constraints:
- Locale-sensitive through `strptime()` weekday/month names.
- Input must match the ctime-style format without timezone.
