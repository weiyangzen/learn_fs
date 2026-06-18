# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/639

## Purpose
This fixture validates a panic-on-warning report in `free_netdev` caused by reference tracker cleanup.

## Important APIs, types, and functions
Key frames include `ref_tracker_dir_exit`, `free_netdev`, `netdev_run_todo`, `default_device_exit_batch`, `ops_exit_list`, `cleanup_net`, `process_one_work`, `worker_thread`, `panic`, and `__warn`.

## Control flow
Network namespace cleanup runs in a workqueue, releases network devices, and reference-tracker exit detects leaked or inconsistent references, causing a warning and panic.

## State and persistence behavior
The file persists workqueue context, network namespace cleanup stack, and `PANICKED: Y`.

## Dependencies and integration points
It tests warning parsing for ref-tracker diagnostics during netdev teardown and panic-on-warn handling.

## Risks and test signals
The parser must choose `free_netdev` as the warning site and retain the panic marker.
