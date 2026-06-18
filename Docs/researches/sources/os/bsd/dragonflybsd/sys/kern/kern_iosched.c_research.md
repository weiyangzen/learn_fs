# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_iosched.c

## Role

Implements a small per-thread/per-CPU I/O scheduling pressure adjustment layer used before buffer-cache write or inode-modifying operations. It tracks recent write bytes, computes each thread's share of outstanding write pressure, and waits on dirty-buffer thresholds proportionally.

## Major Entry Points

- `bwillwrite(int bytes)` is called before intended writes. It invokes `bd_heatup()`, charges bytes to the current thread with `badjiosched()`, computes a dirty-buffer wait target from `hidirtybufspace`, and calls `bd_wait()`.
- `bwillread(int bytes)` is currently a no-op placeholder.
- `bwillinode(int n)` is called before inode-modifying operations. It uses a page-sized charge, scales the heatup count by the computed factor, and waits.
- `biosched_done(thread_t td)` clears a thread's outstanding write-byte accounting and subtracts it from the current CPU bucket.

## Internal Mechanics

- `ioscpu[SMP_MAXCPU]` stores per-CPU aggregate write-byte pressure.
- `badjiosched()` sums all CPU totals, caps additions to avoid `size_t` overflow, updates `td->td_iosdata.iowbytes`, decays the thread and CPU totals based on ticks elapsed up to a ten-second window, and computes a percentage share.
- Debug sysctl `iosched.debug` can print per-thread factor information.

## VFS/File-System Relevance

- This file is directly related to write throttling and dirty buffer pressure, which affects filesystem writeback and metadata-heavy workloads.
- `bwillinode()` indicates metadata/inode operations are intentionally included in I/O pressure accounting even without a byte count from the caller.

## Research Notes

- The algorithm is intentionally simple and approximate; it uses current CPU accounting in `biosched_done()` and in decay, so migration behavior is worth checking if analyzing fairness.
- Comments contain misspellings of "integer"; no behavioral impact.
