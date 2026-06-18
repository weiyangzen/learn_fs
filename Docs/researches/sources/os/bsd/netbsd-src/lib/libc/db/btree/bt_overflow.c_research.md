# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_overflow.c

Read completely: 233 lines.

This implements overflow storage for large btree keys/data. `__ovfl_put` stores a DBT across a linked chain of overflow pages; `__ovfl_get` reads the chain into a reusable buffer; `__ovfl_delete` frees the chain unless the first page is marked `P_PRESERVE`.

Important interactions: leaf/internal items store overflow references as `{pgno_t, uint32_t size}` byte strings. Delete and put paths use these helpers for records larger than the page threshold.

Security/reliability notes: comments note wasted space on the final overflow page and that failed later inserts may leak newly allocated overflow pages. Corrupt overflow chains could cause bad page traversal.
