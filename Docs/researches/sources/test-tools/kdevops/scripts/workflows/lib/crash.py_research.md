# sources/test-tools/kdevops/scripts/workflows/lib/crash.py

## Purpose
Implements kernel crash, warning, and filesystem corruption detection for kdevops hosts, with log collection from guestfs console logs, systemd remote journals, or SSH journalctl and optional libvirt reset.

## Important APIs and types
`KernelCrashWatchdog` is the main class. Important methods include `normalize_kernel_snippet()`, `get_qr_ascii()`, `load_known_crashes()`, `is_known_crash()`, `try_remote_journal()`, `convert_console_log()`, `check_host_reachable()`, `collect_journal()`, `detect_crash()`, `detect_filesystem_corruption()`, `infer_fstests_state()`, `extract_kernel_snippet()`, `decode_log_output()`, `save_log()`, `reset_host_now()`, `wait_for_ssh()`, `next_issue_filename()`, and `check_and_reset_host()`.

## Control flow
Construction reads `extra_vars.yaml` for provider, journal, guestfs, and topdir settings, then loads known issue hashes from existing crash files. `check_and_reset_host()` filters stale issue files by boot time, collects logs using console, remote journal, then SSH according to method/config, normalizes logs, optionally trims already-seen console lines, infers fstests context, saves warnings if requested, suppresses expected fstests corruption, extracts a relevant snippet, writes a new issue file with a QR code, decodes stack traces when possible, resets libvirt hosts, and waits for SSH.

## State and persistence
Persists numbered `journal-XXXX.crash`, `.corruption`, `.crash_and_corruption`, `.warning`, and decoded variants under `output_dir/host`. Maintains known-crash hashes in memory and may remove stale files older than last boot.

## Dependencies and integration
Uses PyYAML, qrcode, SSH, journalctl, guestfs console logs, libvirt `virsh`, Ansible wait_for_connection, and `linux/scripts/decode_stacktrace.sh`.

## Risks and test signals
Detection is regex-based and broad; false positives can reset hosts. `warnings` list is unused, so warning-only reset suppression relies on `warning_file`. The intentional-corruption list must stay current with fstests. Test with synthetic logs for panic, warning, benign warning, expected and unexpected corruption, duplicate issue suppression, and `--no-reset`.
