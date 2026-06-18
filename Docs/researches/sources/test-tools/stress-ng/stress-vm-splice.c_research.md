# sources/test-tools/stress-ng/stress-vm-splice.c

## Purpose
Implements `vm-splice`, a Linux VM/pipe stressor that exercises `vmsplice()` from memory to pipe and pipe to memory while measuring throughput and call rate.

## Important APIs, types, and functions
`stress_vm_splice()` is compiled when `HAVE_VMSPLICE` and `SPLICE_F_MOVE` exist. `opts[]` exposes `vm-splice-bytes`. The worker uses `stress_mmap_populate()`, `pipe()`, `open("/dev/null")`, `vmsplice()`, `splice()`, `write()`, `stress_prime64_get()`, and `stress_metrics_set()`.

## Control flow
The stressor sizes a page-aligned buffer per instance, maps a main iovec buffer and one check page, creates a pipe, opens `/dev/null`, then synchronizes. Each loop `vmsplice()`s memory to the pipe, `splice()`s it to `/dev/null`, writes a check value into the pipe, `vmsplice()`s from pipe to memory, validates the first word, updates counters, and increments bogo ops.

## State and persistence
Runtime state is local mappings, fds, a moving check value, byte/call counters, timing accumulators, and return code. All mappings and fds are cleaned up; no persistent state is created.

## Dependencies and integration points
Registered as `stress_vm_splice_info` with `CLASS_VM | CLASS_PIPE_IO | CLASS_OS`, `VERIFY_ALWAYS`, and memory-size option parsing. Without `vmsplice()` or `SPLICE_F_MOVE`, it registers as unimplemented.

## Risks and edge cases
Mappings can fail under memory pressure and return `EXIT_NO_RESOURCE`. Pipe or `/dev/null` failures are hard failures. Runtime splice errors break the loop. The data check is a sentinel first-word verification, not an exhaustive buffer compare.

## Test signals
Failure signal is a check-pattern mismatch. Metrics are `MB per sec vm-splice rate` and `vm-splice calls per sec`.
