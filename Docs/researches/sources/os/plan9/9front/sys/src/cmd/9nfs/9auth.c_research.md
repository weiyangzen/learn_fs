# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/9auth.c

This standalone utility interacts with a mounted 9nfs authentication file for a user.

Key behavior:
- Parses options `-D`, `-d`, and `-r root`.
- Constructs an auth file path as `<root>/#<username>`.
- With `-d`, creates/truncates the file and exits.
- Otherwise opens the file read/write, reads a network challenge, prompts for a response, rewinds, and writes the response.

Important interactions:
- Uses Unix/POSIX headers rather than Plan 9 headers, suggesting hosted utility behavior.
- Works with authentication pseudo-files exposed by the NFS/9P bridge.

Research notes:
- Default root is `/n/emelie`.
- Challenge and response buffers are `NETCHLEN` bytes.
