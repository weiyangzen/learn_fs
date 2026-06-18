# File Research: sources/os/linux/linux/block/blk-timeout.c

## Scope

This file implements generic request timeout setup and explicit abort handling, plus optional fault injection support for fake I/O timeouts.

## Core APIs

- With `CONFIG_FAIL_IO_TIMEOUT`:
  - `fail_io_timeout` fault attribute can be configured by `fail_io_timeout=`.
  - `__blk_should_fake_timeout()` returns `should_fail()` and is exported.
  - `fail_io_timeout_debugfs()` creates debugfs controls.
  - `part_timeout_show()` and `part_timeout_store()` expose partition/device fail-I/O timeout toggling through `QUEUE_FLAG_FAIL_IO`.
- `blk_abort_request()` sets the request deadline to `jiffies` and schedules `q->timeout_work`, forcing timeout recovery scanning.
- `blk_timeout_init()` initializes `blk_timeout_mask` from rounded `HZ`.
- `blk_rq_timeout()` caps requested expiry at `jiffies + BLK_MAX_TIMEOUT` after rough rounding.
- `blk_add_timer()` initializes a request timeout from `q->rq_timeout` if needed, clears `RQF_TIMED_OUT`, writes `req->deadline`, rounds/caps expiry, and updates `q->timeout` if the new expiry is earlier enough.

## Dependencies and Invariants

- Uses `kblockd_schedule_work()` for timeout work and Linux timer/jiffies helpers.
- The timeout timer is queue-wide; individual requests carry `deadline`.
- Timer changes intentionally tolerate slack (`HZ / 2`) to avoid repeatedly modifying timers for insignificant rounded differences.
- `blk_abort_request()` uses `WRITE_ONCE()` and avoids heavy synchronization because timeout scanning only needs to observe an immediate deadline.
