# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mbuf_marshaling.c

This file provides SMB mbuf-chain marshaling and unmarshaling. It is the format-string engine used to encode and decode SMB protocol fields, strings, vardata blocks, UIOs, mbufs, and time formats.

Key responsibilities:
- Decodes data from `mbuf_chain_t` using SMB-specific format strings.
- Encodes data into `mbuf_chain_t` with dynamic mbuf growth.
- Supports SMB1 and SMB2 signatures.
- Handles little-endian 8/16/32/64-bit scalar access across mbuf boundaries.
- Handles special “odd” 64-bit field layout used by SMB lock large-file records.
- Converts OEM and UTF-16 strings to/from internal UTF-8.
- Supports alignment, skip, peek, poke, copy, and append operations.
- Exposes direct UIO/vardata views over mbuf data.

Important public functions:
- `smb_mbc_vdecodef`, `smb_mbc_decodef`, `smb_mbc_peek`.
- `smb_mbc_vencodef`, `smb_mbc_encodef`, `smb_mbc_poke`.
- `smb_mbc_copy`.
- `smb_mbc_put_mem`.
- `smb_mbc_put_align`.

Format-string highlights:
- `%` supplies `smb_request_t` and determines Unicode mode.
- `M` and `N` validate/emit SMB1 and SMB2 signatures.
- `b/c/w/l/q/Q` handle scalar and byte-buffer fields.
- `u/s/U/L/A/S/P` handle OEM/Unicode/tagged strings.
- `B/D/V` handle vardata blocks and UIO setup.
- `Y/y` convert DOS date/time ordering variants.
- `.` skips or emits zero padding; `,` is Unicode-aware padding/skipping.
- `C/m` represent mbuf-chain and mbuf transfer paths, though mbuf decode is not implemented.

Memory and lifetime:
- Encode paths allocate mbufs as needed up to `mbc->max_bytes`.
- Decoded strings are allocated from the request storage arena with `smb_srm_zalloc`.
- Temporary conversion buffers are allocated with `smb_mem_alloc/zalloc/realloc` and freed before return.
- `mbc_marshal_put_mbufs` always consumes or frees the mbuf chain passed to it.
- `mbc_marshal_put_uio` wraps existing UIO buffers as external mbufs with a no-op free callback.

Edge cases and protections:
- `MBC_ROOM_FOR` and `mbc_marshal_make_room` enforce chain bounds.
- Unicode strings align to a 16-bit boundary before reading/writing.
- OEM string decode caps unspecified strings at 0xffff bytes.
- `smb_mbc_poke` and `smb_mbc_peek` use shadow chains so original offsets are unchanged.
- `mbc_marshal_get_mbufs` is explicitly not implemented, so decode formats requiring raw mbuf extraction fail.
- `smb_mbc_copy` validates source offset and length before copying.
