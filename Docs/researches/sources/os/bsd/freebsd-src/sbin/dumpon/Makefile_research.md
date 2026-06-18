# File Research: sources/os/bsd/freebsd-src/sbin/dumpon/Makefile

Build definition for `dumpon`.

Configuration:
- Includes `src.opts.mk`.
- `PACKAGE=runtime`
- `PROG=dumpon`
- Installs `dumpon.8`.
- If `MK_OPENSSL != no`, links `libcrypto` and defines `HAVE_CRYPTO`.
- Sets `OPENSSL_API_COMPAT=0x10100000L`.

Role:
- Builds the kernel dump-device configuration utility implemented by `dumpon.c`.
