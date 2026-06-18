## sources/user-network-fs/blobfuse2/docker/Dockerfile

Purpose: Builds an Ubuntu 22.04 container image containing blobfuse2, sample config, FUSE3, syslog/logrotate config, and mount/unmount helper scripts.

Important flow: Starts from Microsoft mirror Ubuntu 22.04, creates `/usr/share/blobfuse2`, copies `blobfuse2` and `config.yaml`, installs `ca-certificates`, `vim`, `rsyslog`, and `fuse3`, enables `user_allow_other`, copies rsyslog and logrotate snippets, creates `/mnt/blobfuse_mnt` and `/tmp/blobfuse_temp` with broad permissions, writes shell scripts for mount and unmount, symlinks them as `fuse` and `unfuse`, and enters via `bash fuse`.

State and persistence: Runtime mount point and temp cache are inside the container. Credentials are expected via environment variables referenced by config or storage component.

Dependencies and integration: Requires a prebuilt local `blobfuse2` binary and support files copied by build scripts.

Risks: Runs with FUSE privileges when launched. Scripts are generated with `echo`, permissions are `777`, and entrypoint mounts in foreground. No health checks or non-root hardening. Docker scripts provide the main test signal.
