# sources/test-tools/crashmonkey/code/testing/log_on_off.c

Purpose: minimal utility to verify that the wrapper device can be opened and accepts log on/off ioctls.

Important APIs/control flow: opens `/dev/hwm1`, calls `HWM_LOG_ON`, calls `HWM_LOG_OFF`, closes the fd, and exits.

State and persistence behavior: toggles the kernel wrapper's volatile `Device.log_on` flag. It does not inspect logs or write workload data.

Dependencies and integration: assumes the hwm module is already inserted and exposes `/dev/hwm1`; includes `disk_wrapper_ioctl.h`.

Risks: the current wrapper names the disk `hwm` and `Tester` opens `/dev/hwm`, so `/dev/hwm1` may be stale. Return values from ioctls are ignored. Missing `unistd.h` for `close()` in strict builds.

Test signals: useful as a smoke test only; a stronger test should verify that writes are logged between on/off boundaries.
