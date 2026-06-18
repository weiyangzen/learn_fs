# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_mchain.c

## Purpose
Provides `libmchain`, helper routines for constructing and parsing mbuf chains. These helpers are commonly useful for network/filesystem protocol code that needs endian-aware serialization into mbufs.

## Main Interfaces
Write-side `mbchain`:
- `mb_init()`, `mb_initm()`, `mb_done()`, `mb_detach()`, `mb_fixhdr()`.
- `mb_reserve()`, `mb_put_padbyte()`.
- Integer writers: `mb_put_uint8`, `mb_put_uint16be/le`, `mb_put_uint32be/le`, `mb_put_int64be/le`.
- Bulk writers: `mb_put_mem()`, `mb_put_mbuf()`, `mb_put_uio()`.

Read-side `mdchain`:
- `md_init()`, `md_initm()`, `md_done()`.
- Record handling: `md_append_record()`, `md_next_record()`.
- Integer readers: `md_get_uint8`, `md_get_uint16`, endian-specific 16/32/64-bit helpers.
- Bulk readers: `md_get_mem()`, `md_get_mbuf()`, `md_get_uio()`.

## Implementation Notes
`mb_reserve()` grows the chain when current trailing space is insufficient and panics for reservations larger than `MLEN`. `mb_put_mem()` supports system, user, inline byte-copy, zero-fill, and custom copy callbacks. `mb_put_uio()` advances the uio vectors and residuals as it copies.

`md_get_mem()` walks mbufs, detects incomplete chains as `EBADRPC`, and supports skipping by passing `target == NULL`. `md_get_mbuf()` copies a subrange using `m_copym()` and advances the parser.

## Dependencies
Uses mbuf APIs, endian conversion, `copyin`/`copyout`, uio, and module/feature declarations.

## Research Notes
This is a protocol marshalling utility. It is not filesystem-specific, but it supports kernel subsystems that exchange structured records over mbufs.
