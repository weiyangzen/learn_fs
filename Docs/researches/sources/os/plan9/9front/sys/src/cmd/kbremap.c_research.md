# File Research: sources/os/plan9/9front/sys/src/cmd/kbremap.c

Small keyboard-map cycling filter. It installs an initial map, appends a synthetic `Kswitch` mapping to `/dev/kbmap`, then reads keyboard event records from stdin. When it sees a `c` event whose rune equals `Kswitch`, it advances to the next map file argument and rewrites `/dev/kbmap`; all other events are passed through unchanged.

Options `-m` and `-k` choose the modifier and scancode for the switching key. The program `chdir`s to `/sys/lib/kbmap`, so map names can be relative. Like `kbmap.c`, its writer avoids half-line updates. It is useful in a pipeline where keyboard events flow through the remapper.
