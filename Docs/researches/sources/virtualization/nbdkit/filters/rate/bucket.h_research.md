# File Research: sources/virtualization/nbdkit/filters/rate/bucket.h

This header declares `struct bucket` and the token-bucket API used by `rate.c`: `bucket_init`, `bucket_adjust_rate`, and `bucket_run`. Comments document that capacity is expressed in rate-equivalent seconds and that callers must retry `bucket_run` after sleeping because another thread may consume replenished tokens first.

The API is deliberately stateful and synchronization-free; callers are responsible for locking around bucket access, which `rate.c` does with per-bucket mutexes.
