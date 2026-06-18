# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/edonr_zfs.c

## Role

Adapts the Edon-R hash implementation to the ZFS ABD/zio checksum interface.

## Native Checksum

`abd_checksum_edonr_native()` copies a preinitialized `EdonRState` template, iterates ABD data with `abd_iterate_func()`, feeds bit lengths to `EdonRUpdate()`, finalizes a 512-bit digest, and copies the first four 64-bit words into `zio_cksum_t`.

## Salted Template

`abd_checksum_edonr_tmpl_init()` expands the checksum salt to one Edon-R block by computing `H(salt) || H(H(salt))`, initializes an Edon-R context, feeds the expanded salt block as a MAC-like key, and returns that context as the checksum template. `abd_checksum_edonr_tmpl_free()` zeros and frees it.

## Byteswap Path

`abd_checksum_edonr_byteswap()` calls the native routine into a local `tmp`, then intends to byteswap the words for alternate endian use. As written, it byteswaps `zcp->zc_word[]` rather than `tmp.zc_word[]`, leaving the local native checksum unused. This is a notable implementation issue in this file.
