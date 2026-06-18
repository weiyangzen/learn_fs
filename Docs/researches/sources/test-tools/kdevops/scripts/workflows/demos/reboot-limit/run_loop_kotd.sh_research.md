# sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/run_loop_kotd.sh

## Purpose
Placeholder KOTD wrapper for reboot-limit loop testing.

## Important APIs and control flow
The script ensures `TOPDIR`, sources `.config` and `scripts/lib.sh`, sets `TARGET_HOSTS` to `baseline` or the first argument, prints that kernel-of-the-day updates are not implemented, and invokes `${TOPDIR}/scripts/workflows/demos/reboot-limit/run_loop.sh`.

## State and dependencies
Shares the same persistence and dependencies as `run_loop.sh`; `TARGET_HOSTS` is not exported in this script, so its effect depends on downstream environment behavior.

## Integration points
Used as a compatibility entry point for workflows that still reference a KOTD reboot-limit loop.

## Risks and test signals
The main risk is assuming KOTD updates happen; the script explicitly does not implement them. Test with minimal reboot count and confirm the standard loop runs.
