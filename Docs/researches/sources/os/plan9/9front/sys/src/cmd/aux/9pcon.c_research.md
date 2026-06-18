# File Research: sources/os/plan9/9front/sys/src/cmd/aux/9pcon.c

Interactive 9P protocol console. It connects to a 9P endpoint, lets the user type textual 9P requests/responses, serializes `Fcall`s, prints server messages, and supports scripting.

Connection modes:
- Open an existing `/srv/service` or file path.
- `-c command` runs an rc command connected by a pipe.
- `-n networkaddress` dials a network 9P service.
- `-m` sets message buffer size.
- `-a` enables response assertion mode.

Important behavior:
- `watch()` continuously reads server 9P messages using `read9pmsg`, decodes with `convM2S`, and prints `%F`.
- Command parser supports most 9P `T*` and `R*` messages, including version, auth, attach, walk, open, create, read, write, clunk, remove, stat, wstat.
- `strtoqid()` parses qids from textual `{path,vers,type}` forms.
- `twstat()` builds `Dir` data and marshals it with `convD2M`.
- Scripting commands: `.` sources a file, `def`/`end` define macro functions, `nexttag` sets tag generator.
- `run()` serializes requests with `convS2M`; for `-a`, expected `R*` messages are compared to server messages received via `rendezvous`.

Filesystem relevance:
- Direct manual exerciser for 9P filesystem protocol endpoints.
- Useful for debugging file servers, namespace services, and protocol-level behavior.
