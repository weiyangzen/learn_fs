# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_util.h

## Purpose

`impl/ibtl_util.h` declares private IBTF helper routines for timeout conversion and logging/debug output.

## Main Interfaces

`ibt_usec2ib()` converts microseconds to the InfiniBand 6-bit timeout exponent using the protocol formula `time = 4.096us * 2^exp`. `ibt_ib2usec()` converts the exponent back to microseconds.

The logging section defines log levels `IBTF_LOG_L0` through `IBTF_LOG_L5` plus `IBTF_LOG_LINTR`, describing major errors, sysadmin-facing messages, debug traces, and interrupt-context messages. Debug builds expose `ibtl_dprintf_intr()`, `ibtl_dprintf5()`, `ibtl_dprintf4()`, and `ibtl_dprintf3()`; non-debug builds compile these to no-ops. Levels 0 through 2 remain declared through `ibtl_dprintf0()`, `ibtl_dprintf1()`, and `ibtl_dprintf2()`.

## Research Notes

This is a small support header. The timeout conversion functions are used wherever CM/path/channel timers must map between illumos clock values and IB protocol encodings.
