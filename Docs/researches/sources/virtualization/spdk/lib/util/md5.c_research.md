# File Research: sources/virtualization/spdk/lib/util/md5.c

This file wraps OpenSSL EVP MD5 operations behind SPDK’s `spdk_md5ctx`.

`spdk_md5init()` validates the context, allocates an `EVP_MD_CTX`, initializes it for `EVP_md5()`, and destroys the context on initialization failure. `spdk_md5update()` ignores null data or zero length as a successful no-op, otherwise delegates to `EVP_DigestUpdate()`. `spdk_md5final()` finalizes into the caller-provided digest buffer, destroys the EVP context, and clears the stored pointer.

Return conventions mix SPDK-style `-1` validation failures with OpenSSL’s `1` success / `0` failure for update/final calls. Callers need to treat nonpositive values carefully.
