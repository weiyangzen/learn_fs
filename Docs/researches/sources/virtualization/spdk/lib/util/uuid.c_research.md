# File Research: sources/virtualization/spdk/lib/util/uuid.c

This file wraps platform UUID handling and implements UUIDv5/SHA1 generation fallback.

When `SPDK_CONFIG_HAVE_LIBUUID` is available, it statically asserts `struct spdk_uuid` matches `uuid_t` and delegates parse, lower-case format, compare, generate, copy, null test, and null set to libuuid.

On FreeBSD, it uses `<uuid.h>` equivalents. The parse wrapper rejects empty strings explicitly to match Linux libuuid behavior. Formatting uses `uuid_to_string()`, copies into the caller buffer, and frees the library-allocated string.

`spdk_uuid_generate_sha1()` uses `uuid_generate_sha1()` when configured. Otherwise it computes SHA1 over namespace UUID bytes plus the supplied name using OpenSSL EVP, copies the first 16 digest bytes into the UUID, and sets version 5 and RFC4122 variant bits in raw bytes 6 and 8.

The main invariants are buffer size `SPDK_UUID_STRING_LEN`, cross-platform behavior consistency for empty strings, and correct version/variant bit setting for SHA1-generated UUIDs.
