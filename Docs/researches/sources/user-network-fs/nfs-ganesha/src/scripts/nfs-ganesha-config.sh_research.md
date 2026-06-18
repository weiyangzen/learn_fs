# sources/user-network-fs/nfs-ganesha/src/scripts/nfs-ganesha-config.sh

## Purpose

`nfs-ganesha-config.sh` prepares runtime environment configuration for the systemd Ganesha service by reading distro-specific config files and generating run/default variables.

## Important APIs, Types, and Functions

Shell variables include `CONFIGFILE`, `RUNCONFIG`, `EPOCH_EXEC`, `NODEID_EXEC`, `NOFILE`, `EPOCHVALUE`, `NODEID`, `NOFILE_CONF`, `NUMACTL`, and `NUMAOPTS`. There are no shell functions.

## Control Flow

The script chooses `/etc/sysconfig/ganesha` and `/run/sysconfig/ganesha`, falling back to Debian/Ubuntu paths when the sysconfig directory is absent. If the config file is readable, it sources it, optionally runs epoch/node-ID executables, writes a systemd `LimitNOFILE` drop-in when `NOFILE` is set, reloads systemd, creates the run config directory, and writes the original config plus computed `EPOCH`, `GNODEID`, and NUMA variables.

## State and Persistence Behavior

It writes `/run/sysconfig/ganesha` or `/etc/default/nfs-ganesha` and may write `/lib/systemd/system/nfs-ganesha.service.d/10-nofile.conf`. It may invoke epoch helpers that update their own generation files.

## Dependencies and Integration Points

It depends on POSIX shell, systemd, optional `numactl`, and distro config files. It integrates with systemd service startup and variables consumed by the NFS-Ganesha unit.

## Risks and Edge Cases

The script sources config files directly, so they execute shell code. Several variable expansions are unquoted, making paths with spaces unsafe. Writing a drop-in under `/lib/systemd/system` may conflict with distro packaging expectations. The Debian fallback writes to `/etc/default`, which is persistent rather than `/run`.

## Test Signals

Shell tests should run in a temp root or container with mocked config files, epoch/node commands, numactl, and systemctl. Verify generated environment lines and NOFILE drop-in behavior.
