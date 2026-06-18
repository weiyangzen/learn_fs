# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevsc.c

Alternative `%stdin%`, `%stdout%`, and `%stderr%` IODevice implementation using procedure-stream callouts rather than direct C stdio file streams. It defines the same special devices and public `zget_*` helpers as `ziodevs.c`.

`stdin_open` creates a read procedure stream with literal integer `0` as a marker, allocates a buffer, sets `min_left` to zero, and caches it in `ref_stdin`. `stdout_open` and `stderr_open` create write procedure streams marked by literal integers `1` and `2`. `stdio_close` invokes the saved close/flush procedure, then bumps stream IDs so old file objects become invalid after close.

`zis_stdin` recognizes stdin by checking for a valid reading procedure stream whose procedure marker is literal integer `0`. This variant is used where standard streams are mediated by interpreter callouts instead of direct platform handles.
