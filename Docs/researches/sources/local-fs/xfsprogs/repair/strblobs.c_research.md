# File Research: sources/local-fs/xfsprogs/repair/strblobs.c

Implements deduplicated storage of length-explicit strings in an `xfblob`.

Key structures:
- `struct strblob_hashent`: hash table entry with blob cookie, string length, directory hash, and next pointer.
- `struct strblobs`: owns an `xfblob`, bucket count, and flexible bucket array.

Core API:
- `strblobs_init` creates an `xfblob` and hash table.
- `strblobs_destroy` frees hash entries and destroys blob storage.
- `strblobs_store` deduplicates by lookup, stores new strings in the blob, and records the cookie in the hash table.
- `strblobs_lookup` searches by hash/length and then loads candidates for byte comparison.
- `strblobs_load` retrieves string bytes by cookie.

Important behavior:
- Hash is an accelerator only; exact byte comparison prevents false dedupe.
- Returns positive errno-style values to callers while wrapping negative libxfs `xfblob` returns.
- Intended for repair subsystems that need compact temporary storage for repeated strings.
