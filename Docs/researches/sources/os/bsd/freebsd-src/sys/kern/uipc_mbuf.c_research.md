# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_mbuf.c

## Summary
Implements core FreeBSD mbuf chain manipulation: packet-header setup, external storage sharing, copying, splitting, trimming, pullup/copyup, device/uio conversion, defragmentation, unmapped external-page support, writable unsharing, and optional profiling/stress helpers.

## Main Responsibilities
- Maintains maximum link/protocol header sizing and exposes sysctls.
- Duplicates and releases external mbuf storage references.
- Moves, duplicates, and demotes packet headers and packet tags.
- Copies, appends, trims, splits, concatenates, and linearizes mbuf chains.
- Handles mapped and unmapped (`M_EXTPG`) mbufs for copy/apply/uio paths.
- Builds mbufs from device buffers or `uio` data.
- Defragments or collapses chains to satisfy fragment limits.
- Creates writable copies of shared external buffers.
- Provides optional mbuf stress fragmentation and profiling.

## Key APIs
- Header/storage: `mb_dupcl()`, `m_pkthdr_init()`, `m_move_pkthdr()`, `m_dup_pkthdr()`, `m_demote_pkthdr()`, `m_demote()`.
- Chain copy/edit: `m_prepend()`, `m_copym()`, `m_copypacket()`, `m_dup()`, `m_cat()`, `m_catpkt()`, `m_adj()`, `m_adj_decap()`.
- Linearization/splitting: `m_pullup()`, `m_copyup()`, `m_split()`, `mc_split()`, `m_collapse()`, `m_defrag()`.
- Data movement: `m_copydata()`, `m_copyback()`, `m_append()`, `m_apply()`, `m_devget()`, `m_uiotombuf()`, `mc_uiotomc()`, `m_mbuftouio()`, `m_unmapped_uiomove()`.
- Utility/debug: `m_getptr()`, `m_print()`, `m_fixhdr()`, `m_length()`, `m_sanity()`, `m_unshare()`.

## Important Behavior
`mb_dupcl()` shares `M_EXT` or `M_EXTPG` backing storage and increments the appropriate embedded or external refcount. `M_EXTPG` copies both the external-page metadata and the smaller `m_ext` portion needed for refcount/free handling.

`m_copym()` and `m_copypacket()` create read-only shared-storage copies when external storage is present. `m_dup()` creates a writable deep copy. `m_unshare()` replaces non-writable external buffers with writable clusters and opportunistically coalesces adjacent data.

`m_pullup()` ensures a leading region is contiguous in one mbuf and may copy extra header bytes up to `max_protohdr`. `m_pulldown()` lives in `uipc_mbuf2.c` and handles contiguous regions at arbitrary offsets.

`m_split()` and `mc_split()` can produce tails sharing external storage with the head. Callers that need to modify the result must check writability.

`m_uiotombuf()` dispatches to unmapped external-page allocation when `M_EXTPG` is requested; otherwise it uses `mc_uiotomc()`. `m_unmapped_uiomove()` walks an external-page mbuf's header, physical pages, and trailer.

`m_defrag()` creates a shortest practical chain and frees the original only after success. `m_collapse()` tries in-place coalescing first, then replaces adjacent mbufs with clusters while preserving the first mbuf and packet header.

## State and Synchronization
Most functions operate on caller-owned mbuf chains and assume external synchronization. External storage sharing uses atomic refcounting when needed. VM page allocation/free paths wire anonymous pages and require the matching external free routine.

## Risks
Many helpers free the input chain on failure while others leave it unchanged; callers must know each contract. Packet-header length and socket/send-tag references must stay consistent when moving or duplicating headers. `M_EXTPG` paths require special handling because data may live in header bytes, physical pages, and trailer bytes rather than a single mapped buffer.
