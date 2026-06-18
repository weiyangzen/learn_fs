# File Research: sources/os/bsd/dragonflybsd/sys/kern/libmchain/subr_mchain.c

Implements `libmchain`, a set of mbuf chain construction and decoding helpers with endian-aware scalar helpers and UIO integration.

Build/module:
- Declares `MODULE_VERSION(libmchain, 1)`.

mbchain write-side APIs:
- `m_fixhdr()`
- `mb_init()`, `mb_initm()`, `mb_done()`, `mb_detach()`, `mb_fixhdr()`
- `mb_reserve()`
- `mb_put_uint8()`, `mb_put_uint16be/le()`, `mb_put_uint32be/le()`, `mb_put_int64be/le()`
- `mb_put_mem()`
- `mb_put_mbuf()`
- `mb_put_uio()`

mdchain read-side APIs:
- `md_init()`, `md_initm()`, `md_done()`
- `md_append_record()`, `md_next_record()`
- `md_get_uint8()`, `md_get_uint16()`, `md_get_uint16be/le()`
- `md_get_uint32()`, `md_get_uint32be/le()`
- `md_get_int64()`, `md_get_int64be/le()`
- `md_get_mem()`
- `md_get_mbuf()`
- `md_get_uio()`

Important behavior:
- `m_fixhdr()` recomputes packet header length across an mbuf chain.
- `mb_init()` creates a header mbuf and initializes chain cursors.
- `mb_reserve()` reserves contiguous space in the current mbuf, allocating another mbuf if needed; sizes greater than `MLEN` panic.
- `mb_put_mem()` copies data into an mbuf chain from system memory, user memory, inline byte loops, zero-fill, or a custom callback.
- `mb_put_uio()` drains a `uio` scatter/gather list into an mbchain and updates `uio_offset`, `uio_resid`, iovec base, and length.
- `md_initm()` initializes a decoder over an existing mbuf chain.
- Record helpers use `m_nextpkt` to chain independent records.
- `md_get_mem()` advances through mbufs, copying out to user/system/inline targets or skipping when target is NULL; incomplete chains return `EBADRPC`.
- `md_get_mbuf()` copies a segment of the current chain with `m_copym()` and advances the decoder.
- `md_get_uio()` copies decoded data into a `uio`.

Filesystem relevance:
- Mostly network/protocol support rather than local filesystem code. It can be relevant to network filesystems or filesystem-related kernel protocols that marshal requests and responses through mbufs and UIOs.
