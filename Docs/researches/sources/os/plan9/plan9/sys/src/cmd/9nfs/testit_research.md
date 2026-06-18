# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/testit

Small rc script for manually starting 9nfs services.

Key responsibilities:
- Mounts `nslocum` via `9fs`.
- Kills existing `8.portmapper` and `8.nfsserver`.
- Removes old service chat files.
- Starts `8.nfsserver` with auth and config options, logging stderr to `/tmp/nfsserver`.
- Starts `8.portmapper`, logging stderr to `/tmp/portmapper`.
- Notes a Unix-side NFSv2 mount command.

Dependencies:
- Plan 9 rc shell, `9fs`, `Kill`, `8.nfsserver`, and `8.portmapper`.

Notable risks:
- Hard-coded hostnames, service names, config path, and mount example make this a local test harness rather than a reusable script.
