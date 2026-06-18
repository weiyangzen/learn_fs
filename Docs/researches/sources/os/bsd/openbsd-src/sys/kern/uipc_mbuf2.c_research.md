# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_mbuf2.c

Additional mbuf contiguity and packet-tag helpers.

`m_pulldown()` ensures a requested `[off, off + len)` region is contiguous within an mbuf chain. It first locates the target mbuf with `m_getptr()`, then returns directly if the data is already contiguous and writable. Otherwise it may split a leading mbuf with `m_dup1()`, copy trailing data into existing trailing or leading space, or allocate a new mbuf/cluster up to `MAXMCLBYTES` and copy the target data into it. On failure it frees the original chain and returns `NULL`, matching the historical mbuf contract for pullup-like operations.

The private `m_dup1()` copies a segment into a new mbuf, optionally preserving packet headers when duplicating from offset zero of a packet-header mbuf. It chooses inline storage or an external cluster depending on length and fails for segments larger than `MAXMCLBYTES`.

The remainder implements packet tags stored in `m_pkthdr.ph_tags`. `m_tag_get()` allocates fixed-size tag objects from `mtagpool`, validates maximum size, and records type/length. `m_tag_prepend()`, `m_tag_delete()`, and `m_tag_delete_chain()` maintain the singly linked tag list and recompute or clear the `ph_tagsset` bitmask. `m_tag_find()`, `m_tag_first()`, and `m_tag_next()` provide lookup/iteration, and `m_tag_copy()`/`m_tag_copy_chain()` duplicate individual tags or full tag lists.

Notable constraints: `m_pulldown()` intentionally destroys the input chain on error; tag type values double as bits in `ph_tagsset`, so tag IDs must fit that representation; and tag-copy failure leaves the destination tag chain empty.
