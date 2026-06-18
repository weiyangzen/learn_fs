# File Research: sources/os/plan9/9front/sys/src/cmd/git/proto.c

Transport and pkt-line layer for git protocol interactions. It parses capabilities, traces pkt-lines when debugging, reads/writes pkt-lines, sends flush packets, parses URIs, and opens local, ssh, git, hjgit/gits, and smart HTTP(S) connections.

HTTP uses `/mnt/web`, sets a git user agent, verifies smart HTTP content type/service advertisement, and switches between read/write phases for POST requests. SSH execs `git-upload-pack` or `git-receive-pack`; git/hjgit/gits use TCP or `tlsclient` and perform a git service handshake. `gitconnect`, `writephase`, `readphase`, and `closeconn` are shared by send/get/serve-style commands.
