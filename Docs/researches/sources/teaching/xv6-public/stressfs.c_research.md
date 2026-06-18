# File Research: sources/teaching/xv6-public/stressfs.c

User-space filesystem/IDE race demonstration.

Behavior:
- Forks up to four processes.
- Each writes twenty 512-byte blocks of `a` data to a distinct `stressfsN` file, then reads them back.
- Comments explain it can expose an IDE queue race if locking in `iderw` is intentionally moved and a spin is inserted.

Role:
- Small stress workload for disk queue and block allocation behavior.
