# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/setenv.c

Implements `setenv(name, value, rewrite)` with libc’s environment locking and owned-buffer tracking. It validates the name, finds or creates an environment slot, honors `rewrite == 0`, reuses an existing owned buffer when large enough, otherwise allocates `name=value`, frees the prior owned value, and updates `environ`.

It rejects invalid names and NULL values with `EINVAL`.
