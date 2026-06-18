# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/csquery.c

Small interactive/batch client for `/net/cs`. It opens the selected connection-server file, writes a dial string, seeks back to offset zero, and prints all reply data.

Command-line behavior defaults to `/net/cs`; with a server path and address arguments it queries each address; without address arguments it reads lines from stdin with a prompt. `-s` suppresses reply printing and only records error status.

Dependencies are only libc/Biobuf and the 9P file interface exposed by `cs.c`; it does not parse replies, translate services, or access NDB directly.

Risk surface is minimal. Input lines are passed verbatim except newline removal; failures are reported via `%r`. Buffering is fixed at 128 bytes per read, but reads loop until EOF.
