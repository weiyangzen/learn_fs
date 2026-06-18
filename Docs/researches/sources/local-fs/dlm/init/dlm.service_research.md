# File Research: sources/local-fs/dlm/init/dlm.service

## Purpose
Systemd unit for the standard `dlm_controld` daemon.

## Behavior
- Requires and starts after `corosync.service` and `sys-kernel-config.mount`.
- Loads the `dlm` kernel module before daemon start.
- Uses `/etc/sysconfig/dlm` for `DLM_CONTROLD_OPTS`.
- Runs `/usr/sbin/dlm_controld --foreground`.
- Uses `Type=notify` and `NotifyAccess=main`.
- Sets `OOMScoreAdjust=-1000`.
- Disables `SendSIGKILL` to avoid killing an active daemon with lockspaces, which could cause fencing.

## Notes
- This unit is for `dlm_controld`, not `dlm_sand`.
