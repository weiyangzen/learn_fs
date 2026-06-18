# File Research: sources/os/plan9/plan9/sys/src/9/port/random.c

Implements a kernel random-byte source based on timing jitter.

Mechanism:
- `randominit` registers `randomclock` as a periodic clock callback every 13 ms and starts a `genrandom` kernel process.
- `genrandom` busy-counts in `rb.randomcount`, yielding when higher priority work exists and sleeping when the ring buffer is full.
- `randomclock` samples `randomcount`, folds bits into `rb.bits`, and emits a byte into a 1024-byte circular buffer after four 2-bit samples.
- `randomread` consumes bytes from the ring, waking the producer when empty/full transitions occur, and mixes output through a cheap LCG-style update to obscure synchronized clock cycles.

State:
- `rb` contains `QLock`, producer/consumer rendezvous points, ring pointers, entropy counters, and PRNG accumulator.

Role:
- Provides random bytes to kernel consumers, likely exposed by a device elsewhere.
