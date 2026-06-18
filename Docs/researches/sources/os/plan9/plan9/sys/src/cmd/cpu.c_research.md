# File Research: sources/os/plan9/plan9/sys/src/cmd/cpu.c

Plan 9 `cpu` client/server command for remote login with namespace export.

Client mode dials a cpu server, negotiates authentication and optional encryption, sends an optional command and current directory, starts local note forwarding, waits for remote filesystem readiness, then execs `exportfs` to serve the local namespace to the remote side. Listener mode authenticates, sets user/home environment, mounts the client export at `/mnt/term`, redirects stdio to `/mnt/term/dev/cons`, and execs an interactive or command shell.

Authentication supports `p9` and `netkey`; p9 mode uses `auth_proxy`, shared secret material, SHA1-derived directional secrets, and `pushssl` when encryption algorithms are enabled. The file also implements a small 9P filesystem mounted into `/dev` exposing `cpunote`, used to forward notes between local and remote processes.
