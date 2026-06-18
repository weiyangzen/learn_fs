# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp_upimutex_impl.h

## Role

Private implementation header for user-priority-inheritance mutex tracking.

## Structure

Includes thread and LWP headers, forward declares `upimutex_t` and `upib_t`, defines hash bucket `upib` and tracked mutex `upimutex`, hash sizing/macros based on `lwpchan_t`, try/block constants, and kernel cleanup prototype.

## Dependencies And Consumers

Consumed by kernel synchronization code implementing user PI mutex behavior. Depends on `kmutex_t`, `_kthread`, `lwp_mutex_t`, `lwpchan_t`, and the global `upimutextab` expected by `UPI_CHAIN()`.

## Important Details

`UPILWPCHAN_HASH()` hashes both lwpchan words and masks into a 512-bucket table. The macros assume side-effect-free `lwpchan` expressions because fields are referenced multiple times.

## Research Notes

Read completely: 75 lines, 2235 bytes.
