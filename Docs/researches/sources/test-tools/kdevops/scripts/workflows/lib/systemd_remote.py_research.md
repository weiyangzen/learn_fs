# sources/test-tools/kdevops/scripts/workflows/lib/systemd_remote.py

## Purpose
Reads systemd-journal-remote files for host kernel versions, current time, and last workflow test markers.

## Important APIs
Exceptions mirror the SSH module. `get_host_ip(host)` resolves SSH config hostname via `ssh -G`. `get_current_time(host)` returns local current time. `get_extra_journals(remote_path, host)` finds rotated/suffixed remote journal files for the host IP. `get_uname(remote_path, host, configured_kernel)` extracts the last `Linux version` line. `get_test(remote_path, host, suite)` extracts the latest `run fstests` or `run blktests` marker. `get_last_fstest()` and `get_last_blktest()` wrap `get_test()`.

## Control flow
The module maps a host to `remote-<ip>.journal`, adds extra matching files, then runs `journalctl --no-pager -k -g ... --file ...`. On missing kernel version it can return the configured kernel fallback.

## State and dependencies
Read-only over `/var/log/journal/remote` style files. Requires `ssh -G`, `journalctl`, file permissions for remote journals, and local time.

## Integration points
Used by `fstests.py` and `fstests_watchdog.py` when systemd remote journal support is configured.

## Risks and test signals
`logger.warning` is referenced without defining `logger`. Current time is local host time, not remote journal host time. Test with complete journal files, rotated extra journals, missing `Linux version`, and missing permissions.
