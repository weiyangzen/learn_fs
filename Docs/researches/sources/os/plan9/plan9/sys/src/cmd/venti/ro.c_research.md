# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/ro.c

Purpose: read-only Venti proxy server.

Behavior:
- Listens as a Venti server and forwards read requests to an upstream Venti server.
- Ping, goodbye, and sync succeed locally.
- Write requests fail with `read-only server`.
- Read requests are handled in separate threads by `readthread`.

Integration points:
- Uses both Venti client and server APIs.
- Wraps read data with `packetforeign` so the response packet owns the allocated buffer.

Risks:
- One thread per read can be high overhead under heavy load.
- Upstream errors are passed as Venti error responses.
