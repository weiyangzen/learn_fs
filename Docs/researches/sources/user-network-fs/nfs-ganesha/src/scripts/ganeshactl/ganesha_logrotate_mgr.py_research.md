# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_logrotate_mgr.py

## Purpose

`ganesha_logrotate_mgr.py` manages logrotate configuration and crontab scheduling for Ganesha logs. It can enable, disable, list, change size/rotation settings, and set a custom crontab entry.

## Important APIs, Types, and Functions

Constants define config paths, default cron entry, default size/rotation, and FSAL-specific log paths. `LogRotateManager` provides `get_os_type`, `is_crontab_entry_present`, backup/restore, crontab add/remove, `list_config`, `generate_logrotate_config`, `update_logrotate_config`, `change_config`, `restart_cron_service`, `enable`, `disable`, and `set_crontab`. `show_help` and `main` implement the CLI.

## Control Flow

`main` selects an action from argv. Enabling backs up any existing config, writes a generated config for the selected FSAL log path, and appends a crontab line. Disabling removes cron entries and restores the backup. Changing requires the cron entry to exist, edits `size` and `rotate` lines, and restarts cron. Setting a crontab removes old entries, adds the new one, and forces logrotate.

## State and Persistence Behavior

The script persistently modifies `/etc/logrotate.d/ganesha`, `/etc/logrotate.d/ganesha.default`, user crontab, and cron service state. It may force log rotation immediately.

## Dependencies and Integration Points

It depends on `os`, `sys`, `subprocess`, `platform`, and `shutil`, plus system programs `crontab`, `logrotate`, and `systemctl`. It integrates with distro cron service names and expected Ganesha log paths.

## Risks and Edge Cases

Crontab edits use shell pipelines and broad grep filtering for `/etc/logrotate.d/ganesha`, which can remove unrelated entries containing that path. `set-crontab` accepts arbitrary text and uses shell execution. Writes are not atomic and require root permissions. `platform` is imported but unused. Restarting `cron`/`crond` may fail on non-systemd or differently named services.

## Test Signals

Use temp paths and monkeypatched subprocess calls to test enable/disable/list/change/set-crontab without touching the host. OS-detection tests should cover Ubuntu, RHEL, and other. Integration tests should verify generated logrotate syntax with `logrotate -d`.
