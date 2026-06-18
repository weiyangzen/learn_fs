<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cap.c -->
# sources/test-tools/stress-ng/stress-cap.c

## Purpose
Implements the `cap` stressor, which exercises Linux capability retrieval and setting APIs against known PIDs, the current worker, parent process, and numeric entries in `/proc`.

## Important APIs, Types, and Functions
`stress_cap_info` registers the stressor or an unimplemented stub when capability headers are unavailable. `stress_capgetset_pid()` wraps `capget()` and optional `capset()` using `_LINUX_CAPABILITY_VERSION_3` and `_LINUX_CAPABILITY_U32S_3`, then probes invalid versions and PIDs plus older capability versions when present. The stressor uses `struct __user_cap_header_struct` and `struct __user_cap_data_struct`.

## Control Flow
`stress_cap()` synchronizes, then loops through fixed PID checks, the current worker with `capset`, the parent PID, and all numeric `/proc` entries. Each `stress_capgetset_pid()` call tolerates ESRCH for non-required PIDs but reports unexpected failures. Bogo count increments inside the helper after each capability test sequence.

## State and Persistence Behavior
The file maintains no persistent state. Per-call capability structs are zeroed on the stack. It reads `/proc` directory entries but writes no files.

## Dependencies and Integration Points
Depends on Linux capability headers, `/proc`, stress-ng logging, sync, bogo, and unused PID helpers. `verify = VERIFY_ALWAYS` makes unexpected syscall behavior visible during stress-ng verification.

## Risks and Edge Cases
PID races are normal while iterating `/proc`; ESRCH handling must distinguish expected missing processes from required PIDs. `capset` can fail due to permissions. Build environments without `sys/capability.h` or version 3 capability definitions receive an unimplemented stressor.

## Test Signals
Successful runs should produce bogo operations without unexpected `capget` or `capset` failures. Test on a normal unprivileged Linux session and a privileged/root session to cover permission differences.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cap.c -->
