<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/managed/config.json -->
# sources/user-network-fs/rclone/contrib/docker-plugin/managed/config.json

## Purpose

`config.json` is the Docker managed-plugin manifest for the rclone volume driver.

## Important APIs, Types, and Functions

It declares the `docker.volumedriver/1.0` interface on `rclone.sock`, grants `CAP_SYS_ADMIN`, exposes `/dev/fuse`, uses host networking, sets `entrypoint` to `rclone serve docker`, and defines configurable args/env/mounts plus propagated mount `/mnt`.

## Control Flow

Docker reads this manifest when installing/enabling the plugin, creates bind mounts for config and cache, injects env vars, and starts the plugin process.

## State and Persistence Behavior

Persistent state resides in host bind mounts under `/var/lib/docker-plugins/rclone/config` and `/var/lib/docker-plugins/rclone/cache`; rclone mounts are propagated from `/mnt`.

## Dependencies and Integration Points

It couples Docker plugin metadata, rclone serve docker, host FUSE, host network namespace, and configurable proxy values.

## Risks and Test Signals

Risks include broad `CAP_SYS_ADMIN`, host networking exposure, bind mount path assumptions, and propagated mount correctness. Tests should validate Docker plugin install, settable env/args, config/cache persistence, and FUSE device availability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/managed/config.json -->
