# File Research: sources/os/plan9/9front/sys/src/cmd/venti/ro.c

Purpose: Read-only Venti proxy server.

Key behavior:
- Listens for Venti requests on one address and connects to an upstream Venti server.
- Passes through ping, goodbye, and sync responses.
- Services read requests in separate threads by reading from upstream and returning packet-backed data.
- Rejects writes with a read-only error.
- Supports verbose logging and separate listen/upstream addresses.

Dependencies:
- Uses Venti server/client APIs, packet foreign buffers, and Plan 9 threading.

Notable details:
- Each read allocates a buffer sized to the requested count and transfers ownership to the response packet.
