# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/hash.h

This header defines `Stringtab` and `Hash` for serialized token-count tables.

`Stringtab` stores linked-list and bucket-chain pointers, token bytes/length, count, and date. `Hash` stores sort status, buckets, bucket/table counts, and the all-entry list.

It declares lookup, sorting, serialization, deserialization, cleanup, and lock-retrying open helpers.
