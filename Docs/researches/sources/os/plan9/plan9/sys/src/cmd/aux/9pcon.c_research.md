# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/9pcon.c

Interactive 9P connection exerciser. It connects to a service file, a shell command (`-c`), or a network address (`-n`), then forks: one process watches and prints incoming Fcalls; the other reads command lines and sends T-messages.

Supports manual construction of `Tversion`, `Tauth`, `Tflush`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, `Twstat`, plus `nexttag`.

Useful for debugging 9P servers by sending arbitrary protocol messages and observing formatted responses.
