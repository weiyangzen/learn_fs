# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/generic_lc_all.c

Read completely: 117 lines.

This file implements `_generic_LC_ALL_setlocale`. It parses either a single locale name applied to all categories or a slash-separated per-category locale query string, calls each category's setlocale handler, and builds the composite `locale->query` string.

Important interactions: registered for `LC_ALL` by `setlocale.c`. It drives all category-specific handlers from `_find_category`, including dummy collate and Citrus-backed categories.

Security/reliability notes: it copies input into a fixed-size `head` buffer with `strlcpy` but does not explicitly check truncation. Slash parsing rejects malformed category counts. It returns NULL if no category load succeeds for a non-NULL request.
