# sources/sync-backup/rsync/inums.h

## Purpose

`inums.h` provides inline numeric formatting wrappers used by debug, itemization, statistics, and logging paths. It centralizes the choice between raw, comma-formatted, and human-readable number rendering while delegating actual formatting to `do_big_num()` and `do_big_dnum()`.

## Important APIs, Types, And Functions

Integer helpers are `big_num(int64 num)`, `comma_num(int64 num)`, and `human_num(int64 num)`. Floating helpers are `big_dnum(double dnum, int decimal_digits)`, `comma_dnum(double dnum, int decimal_digits)`, and `human_dnum(double dnum, int decimal_digits)`.

`comma_num()` and `comma_dnum()` use `human_readable != 0` to request comma/grouped formatting from the underlying formatter. `human_num()` and `human_dnum()` pass the full `human_readable` level, allowing human-readable units when enabled.

## Control Flow

Each inline function immediately calls the appropriate formatter and returns its `char *` result. There is no local allocation or branching beyond reading the global `human_readable`.

## State, Dependencies, And Integration

The functions have no own state, but they depend on the global `human_readable` and on formatter functions that likely return static rotating buffers. Many modules include this header for concise logging, including file-list stats, checksum debug, hashtable debug, hard-link debug, and generator messages.

## Risks

Because results are `char *` values from shared formatter routines, callers should not assume long-lived ownership or unlimited simultaneous formatted values. Output changes when `human_readable` changes globally, so tests should set that option explicitly. Inline definitions in a header mean signature or semantic changes propagate widely at compile time.

## Test Signals

Test raw, comma, and human-readable output for small, large, negative, and floating values; multiple calls in one logging expression if formatter buffers rotate; and behavior with `human_readable` set to 0, 1, and higher levels.
