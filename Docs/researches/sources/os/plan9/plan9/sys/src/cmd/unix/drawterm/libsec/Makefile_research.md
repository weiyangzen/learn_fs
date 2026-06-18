# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/Makefile

Builds `libsec.a` for drawterm. It sets `ROOT=..`, includes `../Make.config`, defines `LIB=libsec.a`, and lists object files for AES, Blowfish, PEM decode, DES modes, DSA, ElGamal, random/prime generation, HMAC, MD4/MD5/SHA1, RC4, RSA, and small-prime support.

The default target builds the static archive by running `$(AR) r $(LIB) $(OFILES)` followed by `$(RANLIB) $(LIB)`. The generic compile rule maps `%.$O` from `%.c` via `$(CC) $(CFLAGS) $*.c`.

Test/helper files present in the directory, such as `egtest.c`, `hmactest.c`, `md4test.c`, `primetest.c`, `rsatest.c`, `readcert.c`, `thumb.c`, and block files like `md5block.c`/`sha1block.c`, are not all represented in this object list. The archive composition is therefore narrower than the directory contents.
