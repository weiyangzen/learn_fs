# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/plan9.c

`plan9.c` is samterm's Plan 9 platform glue.

`getscreen` parses `-a` autoindent and `-i` spaces-indent options, initializes draw, reads `$tabstop`, and clears the screen. `screensize` reads `/dev/screen` geometry.

`snarfswap` exchanges sam's snarf text with `/dev/snarf`, respecting older host protocol snarf limits when `hversion < 2`.

Plumbing support opens the `edit` and `send` ports. `plumbproc` reads plumb messages, `plumbformat` converts supported `showfile` messages into command-window input beginning with `B ` plus optional address, and `plumbstart` launches the reader.

`hostproc` continuously reads host protocol bytes from stdin into double buffers and signals `hostc`; EOF is fatal unless samterm is already exiting. `hoststart` creates the channel and reader process.

`extproc` is a generic external reader using the plumb buffer structure. `dumperrmsg` reports malformed oversized host messages and consumes the current string payload for diagnostics.
