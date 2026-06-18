# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/raperrstr.c

Maps Microsoft Remote Administration Protocol/LANMAN API error numbers to readable messages. The table covers generic access/password errors, service, print, logon, user/group, share, DFS, remoteboot, browser, UPS, and domain join/account policy errors.

`raperrstr(uint err)` scans the table for an exact match and returns `rap: <message>` or a numeric unknown-error string in a static buffer.

Used by RAP wrapper functions in `trans.c` to turn remote API status words into Plan 9 error strings via `werrstr`.

Implementation is intentionally simple: static table, linear search, static return buffer.
