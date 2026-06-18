# sources/test-tools/kdevops/scripts/workflows/blktests/blktests_watchdog.py

## Purpose
Reports blktests progress per host and flags possible hung or timed-out tests.

## Important APIs
`print_blktest_host_status(host, verbose, basedir, config)` combines `kssh.get_uname()`, `blktests.get_section()`, `blktests.get_blktest_host()`, and `blktests.get_last_run_time()` to print either a compact table row or verbose details. `_main()` parses hostfile, host section, and verbosity.

## Control flow
The CLI validates the hostfile and `.config`, computes `basedir`, reads hosts through `blktests.get_hosts()`, prints a table header, and processes each host. Percent complete is current runtime divided by historical runtime when available. Stall state is `Timeout`, `Hung-Stalled`, or `OK`.

## State and dependencies
Read-only over Ansible inventory, `.config`, remote SSH state, dmesg/journal lines, and prior blktests results. Requires the local `lib` package modules.

## Integration points
Used by blktests workflow monitoring and manual watchdog views.

## Risks and test signals
If historical runtime is absent, percent remains zero and stall detection may rely on default thresholds. Remote SSH timeouts map to stall signals. Test with host fixtures running a known blktest, no running process, and a forced timeout.
