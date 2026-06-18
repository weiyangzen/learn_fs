# sources/test-tools/kdevops/scripts/workflows/generic/get_console.py

## Purpose
Provides the get-console entry point for the generic crash watchdog behavior.

## Important APIs and control flow
The file shares the `crash_watchdog.py` implementation pattern: when the invoked program name is `get_console.py`, the watchdog path disables reset, disables warning saving, and requests full log behavior. It delegates log collection to `KernelCrashWatchdog`.

## State and dependencies
Read-only intent, but actual behavior depends on the shared watchdog code and selected method. It may still read guestfs console logs, remote journals, or SSH journal output. Depends on the same Python modules and kdevops inventory/config files as `crash_watchdog.py`.

## Integration points
Used as a convenience command or symlink target for retrieving kernel console output without treating it as a crash response action.

## Risks and test signals
The shared code sets `args.full_log_mode = True`, while the library uses `full_log`; if this file is a copy rather than symlink, confirm the intended flag is actually passed. Test by invoking as `get_console.py` with `--no-reset` behavior and verifying no reset occurs.
