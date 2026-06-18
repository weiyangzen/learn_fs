# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_mbuf2.c

## Summary
Additional mbuf utilities from KAME/WIDE: contiguous-region pull-down support and packet tag management.

## Main Responsibilities
- Implements `m_pulldown` to ensure a byte range is contiguous within an mbuf chain.
- Provides `m_dup1` helper for localized mbuf copying.
- Allocates, frees, prepends, unlinks, deletes, locates, copies, and iterates `struct m_tag` packet tags.
- Initializes tag lists on packet-header mbufs.

## Important Behavior
`m_pulldown` frees the original chain and returns NULL on failure. It avoids modifying shared clusters in place and may split, extend, shift, or allocate an mbuf to make the requested range contiguous.

Packet tags are stored in `m_pkthdr.tags`; callers must pass packet-header mbufs for most tag operations. `m_tag_copy_chain` deletes any existing destination tags before copying from the source.

## Risks
`m_pulldown` has destructive failure semantics, so callers must not use the original chain after NULL. Tag APIs rely on packet-header invariants enforced by assertions. A failed tag-chain copy leaves the destination with no copied tags.
