# File Research: sources/windows/reactos/drivers/filesystems/udfs/unload.cpp

This file defines `UDFDriverUnload`.

Behavior:
- Logs unload.
- Sets `UDF_DATA_FLAGS_BEING_UNLOADED` in `UDFGlobalData.UDFFlags` to prevent further mount operations.
- Enters an infinite loop sleeping for 10 seconds at a time while printing `Poll...`.
- Symbolic link deletion and device-object deletion code is present only as comments.

Notable design points:
- The unload routine does not actually complete. It intentionally waits forever after marking the driver as unloading.
- Because the cleanup code is commented out, this driver cannot unload cleanly through this path as written.
- The unload flag is still meaningful because verification/comparison code checks `UDF_DATA_FLAGS_BEING_UNLOADED` and can reject volumes as wrong-volume during teardown-like states.
