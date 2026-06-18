# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mbuf_util.c

This file implements SMB server mbuf and mbuf-chain allocation/manipulation. It adapts BSD-style mbuf operations to illumos SMB server needs and backs protocol marshaling and network I/O.

Key responsibilities:
- Creates and destroys kmem caches for `mbuf_chain_t`, `mbuf_t`, and mbuf clusters.
- Allocates/frees `mbuf_chain_t`.
- Allocates mbufs from memory buffers, external buffers, kmem-backed buffers, or chains sized for large I/O.
- Builds UIO/iovec views over mbuf chains.
- Trims, attaches, appends, shadows, prepends, adjusts, and frees mbufs.
- Provides cluster allocation/free/reference callbacks used by mbuf macros and network wrapping.

Important functions:
- `smb_mbc_init`, `smb_mbc_fini`.
- `smb_mbc_alloc`, `smb_mbc_free`.
- `smb_mbuf_get`, `smb_mbuf_alloc_ext`, `smb_mbuf_alloc_kmem`, `smb_mbuf_alloc_chain`.
- `smb_get_vdb`.
- `smb_mbuf_allocate`.
- `smb_mbuf_mkuio_cont`, `smb_mbuf_mkuio`.
- `smb_mbuf_trim`.
- `MBC_LENGTH`, `MBC_MAXBYTES`, `MBC_SETUP`, `MBC_INIT`, `MBC_FLUSH`.
- `MBC_ATTACH_MBUF`, `MBC_APPEND_MBUF`, `MBC_ATTACH_BUF`, `MBC_SHADOW_CHAIN`.
- `m_adjust`, `m_prepend`, `m_free`, `m_freem`.
- `smb_mbuf_alloc`, `smb_mbuf_free`, `smb_mbufcl_alloc`, `smb_mbufcl_free`, `smb_mbufcl_ref`.

Performance and allocation behavior:
- `smb_mbuf_alloc_chain` avoids overusing oversized kmem allocations by splitting at `kmem_max_cached`.
- Large kmem-backed mbufs are prepended so shorter front segments are more likely available for copy-heavy protocol headers.
- `smb_mbuf_mkuio_cont` can append mbuf segments after prefilled iovec entries, used by SMB2 signing paths.

Edge cases and protections:
- `MBC_SHADOW_CHAIN` rejects negative offsets/lengths and integer wraparound.
- `smb_mbuf_mkuio_cont` returns `E2BIG` when iovec space is insufficient and `EFAULT` when the mbuf chain is too short.
- `m_adjust` supports only head trimming; tail trimming is handled by `smb_mbuf_trim`.
- `m_prepend` allocates a new mbuf if leading space is insufficient.
- External-buffer free callbacks are responsible for freeing backing storage; no-op callbacks are used for borrowed buffers.
