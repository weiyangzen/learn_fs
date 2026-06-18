# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/movegen.c

Generates invisible movement objects. It consumes text, same, direction, `TO`, `BY`, `FROM`, and `AT` attributes to compute cursor displacement.

Without explicit displacement, it uses `movewid`/`moveht` in the current direction. With `same`, it repeats the previous movement delta.

It records bounds before and after movement, updates `curx/cury`, saves the previous delta, creates a `MOVE` object, and returns it.
