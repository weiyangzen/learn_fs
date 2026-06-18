# File Research: sources/os/plan9/9front/sys/src/cmd/lp/lpsend.c

`lpsend` is a simpler print relay sender. It reads one options line from stdin, spools the rest of stdin to a temp file to know its size, dials a supplied network address, sends the options line, sends the byte count, waits for ACK, sends data, ACKs completion, waits for final ACK, then copies any response to stdout.

It has Plan 9 and non-Plan 9 compatibility sections, uses alarm timeouts for network reads/writes, and temp files under `/tmp`. The protocol is paired with `lpdaemon`’s non-BSD path.
