# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_mbuf2.c

## Summary
Adds mbuf helpers from KAME/WIDE heritage: arbitrary-offset pulldown for contiguous data access and packet tag allocation/copy/delete routines.

## Main Responsibilities
- Implements `m_pulldown()` to make a byte range contiguous within an mbuf chain.
- Provides a local `m_dup1()` helper for copying a slice into a new mbuf.
- Allocates, frees, finds, deletes, and copies packet tags.
- Handles MAC framework special cases for MAC label packet tags.

## Key APIs
- `m_pulldown()`.
- `m_tag_alloc()`, `m_tag_free_default()`, `m_tag_delete()`, `m_tag_delete_chain()`.
- `m_tag_delete_nonpersistent()`, `m_tag_locate()`, `m_tag_copy()`, `m_tag_copy_chain()`.

## Important Behavior
`m_pulldown()` ensures `[off, off + len)` is contiguous. If `offp` is `NULL`, it may split or copy so the returned mbuf starts the target at offset zero; if `offp` is non-NULL, it can return a nonzero offset through `*offp`.

The function handles easy cases by extending into trailing space or leading space when the target mbuf is considered writable, and otherwise allocates a new mbuf or cluster. On error it frees the original chain.

The writability test is intentionally conservative and historically imperfect: regular non-external mbufs are treated as writable, but external storage requires an `EXT_CLUSTER` and `M_WRITABLE()`.

Packet tags are malloc-backed `struct m_tag` objects with data stored immediately after the tag header. Chain copy preserves order and deletes any destination tags before copying.

## State and Synchronization
Packet tag operations assume the caller owns or has locked the mbuf packet header tag list. Tag memory uses the `M_PACKET_TAGS` malloc type. MAC label tags call MAC framework init/copy/destroy hooks.

## Risks
`m_pulldown()` frees the input chain on malformed or too-short input and on allocation failure. Consumers must not continue using the original chain after a `NULL` return. Packet tag copying can fail partway and leaves the destination tag chain empty.
