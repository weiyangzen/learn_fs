# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/hash.c

This file implements the text hash table used by the older bayes tools. `Stringtab` entries are pooled in large chunks, strings are arena-copied, and `Hash` maintains both a hash table and an `all` linked list.

`findstab()` performs move-to-front lookup, creates entries when requested, and grows/rebuilds the bucket table. `sortstab()` merge-sorts entries lexicographically. `Bwritehash()` writes a `# hash table` format, skipping nonpositive and stale entries older than 30 days. `Breadhash()` reads and scales counts, preserving the newest date.

`freehash()` returns string table nodes to the free list and frees bucket storage. `Bopenlock()` retries opening locked files for up to about two minutes.
