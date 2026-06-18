# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/testit

Rc script for manually starting and testing 9nfs services.

Key responsibilities:
- Mounts or prepares the `nslocum` namespace via `9fs`.
- Kills existing `8.portmapper` and `8.nfsserver` processes.
- Removes service chat files.
- Starts `8.nfsserver` with address/config options and `8.portmapper`, redirecting stderr logs.

Role:
- Developer/operator smoke-test helper for NFS server and portmapper setup.

Notable risks:
- Hard-coded host/service names and architecture-prefixed binaries make it environment-specific.
