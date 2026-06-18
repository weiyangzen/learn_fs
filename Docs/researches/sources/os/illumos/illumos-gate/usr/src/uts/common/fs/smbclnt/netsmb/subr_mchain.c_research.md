# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/subr_mchain.c

## Scope

This file implements BSD mbuf-style mbchain/mdchain packing and unpacking on top of illumos STREAMS mblks.

## APIs And Behavior

- Provides UIO helpers `uio_curriovbase()`, `uio_curriovlen()`, and `uio_update()`.
- `m_getblk()` allocates STREAMS mblks with minimum size `MLEN` of 4096 bytes.
- `mb_init()` allocates a new send chain and reserves 4 bytes for a later NetBIOS header.
- `mb_done()`, `mb_initm()`, `mb_detach()`, `m_fixhdr()`, and `mb_fixhdr()` manage mbchain lifetime and length.
- `mb_reserve()` reserves contiguous space in the current mblk, appending blocks as needed.
- `mb_put_*()` functions append fixed-width integers in big/little endian form.
- `mb_put_padbyte()` aligns Unicode strings; `mb_put_align8()` pads to an 8-byte boundary.
- `mb_put_mem()`, `mb_put_mbuf()`, `mb_put_mbchain()`, and `mb_put_uio()` copy system, user, zero, inline, mblk, mbchain, or UIO data into outgoing chains.
- `md_initm()`, `md_done()`, `md_append_record()`, and `md_next_record()` manage receive chains and multi-record responses using `b_next`.
- `md_get_*()` functions decode fixed-width integers.
- `md_get_mem()`, `md_get_mbuf()`, and `md_get_uio()` extract bytes to system/user buffers, copied mblks, or UIOs.
- Solaris shims `m_cat()`, `m_copym()`, `m_pullup()`, `m_split()`, and `md_tell()` emulate mbuf-style operations.

## State And Dependencies

- Uses STREAMS mblk fields `b_rptr`, `b_wptr`, `b_cont`, `b_next`, data-block bounds, `dupmsg`, `dupb`, `adjmsg`, `pullupmsg`, and copyin/copyout.
- Used throughout SMB1/SMB2 request building and response parsing.

## Risks And Invariants

- `mb_init()` intentionally leaves 4 bytes headroom for NetBIOS transport headers.
- `md_done()` frees all chained records, including unusual `b_next` record lists.
- Some inline macros depend on local variable names and are intentionally macro-based because compiler options prevented effective inlining.
- Incorrect mblk splitting/copying can corrupt receive fragment ownership or leak message chains.
