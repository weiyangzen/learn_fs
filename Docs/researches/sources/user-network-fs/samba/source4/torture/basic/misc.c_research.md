# sources/user-network-fs/samba/source4/torture/basic/misc.c

## Purpose
This file contains miscellaneous SMB torture and benchmark utilities: randomized read/write stress, pipe count probing, idle connection/file-handle hold tests, maximum fnum discovery, IOCTL scanning, and an asynchronous multi-connection read/write benchmark.

## Important APIs, types, and functions
Exported entry points include `run_torture()`, `run_pipe_number()`, `torture_holdcon()`, `torture_holdopen()`, `torture_maxfid_test()`, `torture_ioctl_test()`, and `run_benchrw()`. The benchmark uses `enum benchrw_stage`, `struct bench_params`, `struct benchrw_state`, `init_benchrw_params()`, `benchrw_callback()`, `benchrw_rw_callback()`, `benchrw_open()`, `benchrw_mkdir()`, `benchrw_close()`, `async_open_callback()`, and `torture_connect_async()`.

## Control flow
`rw_torture()` coordinates random file writers through a lock file and verifies PID data after repeated writes. `run_pipe_number()` opens `\WKSSVC` until failure. `torture_holdcon()` opens many connections and pings until all die; `torture_holdopen()` opens one file many times then pings forever. `torture_maxfid_test()` creates a directory fanout and opens up to `0x11000` files, then closes and unlinks them. `torture_ioctl_test()` scans device/function values and prints successful IOCTLs.

The `run_benchrw()` path is an event-driven state machine. It initializes UNC targets from settings or an `unclist`, starts async composite connects, cleans/creates per-worker directories, opens files, writes initial blocks, keeps a configured number of parallel read/write requests in flight, closes, deletes test dirs, and disconnects trees.

## State and persistence
The tests create `\torture.lck`, `\torture.N`, `\holdopen.dat`, `\maxfid`, `\ioctl.dat`, and benchmark directories such as `benchrw0`. Several tests are deliberately long-lived or infinite until the server drops connections. Local state is stored in talloc-owned benchmark structs and callbacks.

## Dependencies and integration points
This file touches raw SMB, composite connect APIs, tevent, resolver configuration, command-line credentials, local file loading for `unclist`, and torture runtime settings such as `nprocs`, `retry`, `blocksize`, `writeblocks`, `writeratio`, `parallel_requests`, `host`, and `share`.

## Risks
Some functions are destructive stress tools rather than normal pass/fail unit tests. `torture_holdcon()` and `torture_holdopen()` intentionally loop indefinitely. `torture_maxfid_test()` can create many files and consume server resources. `run_benchrw()` mixes async callbacks with synchronous cleanup and is sensitive to callback state transitions, memory ownership, and event-loop progress.

## Test signals
Signals include data corruption in `rw_torture()`, maximum open pipe/file counts, successful IOCTL discovery lines, benchmark `ERROR` states, tree disconnect failures, and whether all async workers reach `FINISHED`.
