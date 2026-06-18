# File Research: sources/os/plan9/9front/sys/src/cmd/sam/io.c

`io.c` handles file I/O and startup of local or remote `samterm`.

`writef` writes the selected address range to the filename in `genstr`, checks for stale same-name files by device/qid/mtime, rejects append-only targets with existing length, updates clean sequence and file identity after write, and warns about missing final newline.

`readio` loads bytes from `io` into a `File`, either via `bufload` for unread files or by streaming through `loginsert` for existing files. It converts UTF, elides NULs, records file identity, and can load the terminal rasp.

`writeio` writes a file range by reading rune chunks, converting them to bytes, and writing them to `io`. `closeio` closes the descriptor and reports byte/rune count.

`bootterm` starts `samterm` locally using two pipes or execs it over already-connected remote fds. `connectto` starts a remote `sam` via `rx machine rsamname -R ...`, wiring pipes so host and terminal can speak the sam protocol.

`startup` coordinates remote connection, local terminal boot unless `-R`, marks the session downloaded, and sends the protocol version.
