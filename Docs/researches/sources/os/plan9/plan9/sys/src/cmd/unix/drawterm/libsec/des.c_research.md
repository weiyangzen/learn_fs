# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des.c

Core DES implementation. It includes `os.h` and `<libsec.h>`, defines static DES S/P-box combination tables, key compression tables, rotation schedule, and parity conversion data.

Public functions are `block_cipher`, `triple_block_cipher`, `des_key_setup`, `des56to64`, `des64to56`, and `key_setup`. `block_cipher` performs DES over one 8-byte block using a 32-word expanded key and a decrypt/encrypt direction flag. `triple_block_cipher` sequences three DES operations using the bit-encoded E/D ordering constants from `libsec.h`.

`des_key_setup` accepts an 8-byte DES key and fills the 32-word expanded schedule. `key_setup` is a compatibility wrapper for 7-byte keys, converting through `des56to64`; `des64to56` reverses that format conversion.

The file provides the primitive operations used by the CBC/ECB mode wrappers and by the X9.17-style random generator in `genrandom.c`.
