# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevcal.c

Defines the `%Calendar%` IODevice.

`gs_iodev_calendar` is a special IODevice whose only meaningful implementation is `calendar_get_params()`. Most file/device operations are wired to `iodev_no_*` stubs.

`calendar_get_params()` calls `time()` and `localtime()`, converts `tm_year` to calendar year and `tm_mon` to 1-based month, writes fields `Year`, `Month`, `Day`, `Weekday`, `Hour`, `Minute`, and `Second`, then writes a boolean `Running`.

If time acquisition fails, all time fields are zeroed and `Running` is false.

This file has no operator table; it exports an IODevice descriptor.
