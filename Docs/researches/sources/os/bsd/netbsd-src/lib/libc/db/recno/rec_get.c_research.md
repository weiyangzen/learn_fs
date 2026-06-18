# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_get.c

Implements record retrieval and lazy import from backing files. `__rec_get` validates flags and one-based record keys, imports records up to the requested number if not already loaded, searches the btree by zero-based record index, and returns data with `__rec_ret`, retaining or releasing the page depending on `B_DB_LOCK`.

The file also defines backing-file readers. `__rec_fpipe` reads fixed-length records from a `FILE *`, padding short final records with `bt_bval`. `__rec_vpipe` reads delimiter-separated variable records from a `FILE *`, growing `bt_rdata` as needed. `__rec_fmap` and `__rec_vmap` perform analogous fixed/variable imports from an mmap region, advancing `bt_cmap`. All import helpers insert records using `__rec_iput` and set `R_EOF` when the source is exhausted.

Dependencies include `__rec_search`, `__rec_ret`, `__rec_iput`, and recno state configured by `rec_open.c`.

Risks/invariants: record keys are one-based externally and zero-based internally. Variable import treats delimiter bytes as separators and does not include them in stored data.
