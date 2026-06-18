# File Research: sources/virtualization/nbdkit/filters/rate/rate.c

This filter rate-limits read and write bandwidth with global and per-connection token buckets. Configuration supports `rate`, `connection-rate`, dynamic `rate-file`, dynamic `connection-rate-file`, and `burstiness` in seconds.

`.get_ready` initializes global read/write buckets. `.open` initializes per-connection read/write buckets and mutexes. `maybe_adjust` optionally reads the first line of a configured rate file, parses a size value, and updates a bucket under lock. `maybe_sleep` converts byte counts to bits, runs a bucket under lock, and sleeps with `nbdkit_nanosleep` until enough tokens can be obtained.

`rate_pread` applies dynamic global-read adjustment, global read limiting, dynamic per-connection read adjustment, and per-connection read limiting before forwarding. `rate_pwrite` mirrors this for writes. Reads and writes have separate buckets, so the configured limit is enforced independently in each direction.

Operational risks are expected for sleep-based throttling: dynamic rate files are polled per request, system clock jumps can affect refill calculations, and rate units are bits per second derived from byte counts times eight without transport overhead.
