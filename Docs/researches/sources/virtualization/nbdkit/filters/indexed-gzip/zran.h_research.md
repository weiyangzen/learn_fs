# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/zran.h

Defines zran constants, data structures, and helper declarations. `WINSIZE` is 32768 bytes, `CHUNK` is 16384 bytes, and modes are RAW, ZLIB, and GZIP using `inflateInit2()` window-bits values.

`point_t` records an access point’s uncompressed offset, compressed input offset, bit alignment, dictionary length, and saved dictionary window. `struct deflate_index` stores access points, total uncompressed length, compression mode, and a reusable `z_stream`.

Declares free, serialize, deserialize, and access-point append helpers. Also provides a fallback `inflatePreface()` implementation under `NOPRIME` for systems without `inflatePrime()`.
