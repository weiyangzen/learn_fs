# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/nullFilter/nullFilter.c

Minimal null minifilter sample.

Key responsibilities:
- Defines `NULL_FILTER_DATA` with only the registered filter handle.
- Registers a `FLT_REGISTRATION` with no operation callbacks and no context registrations.
- Starts filtering in `DriverEntry`.
- Unregisters in `NullUnload`.
- Allows explicit/manual instance teardown in `NullQueryTeardown`.

Important behavior:
- Because `Operation callbacks` is `NULL`, this filter observes no I/O operations.
- The sample is primarily a skeleton for registration, start, unload, and instance-teardown plumbing.
- `DriverEntry` unregisters the filter if `FltStartFiltering` fails.

Dependencies and risks:
- Depends only on standard FltMgr kernel APIs.
- The code asserts registration success but also handles failure through status returns.
- There is no per-instance or per-operation state.
