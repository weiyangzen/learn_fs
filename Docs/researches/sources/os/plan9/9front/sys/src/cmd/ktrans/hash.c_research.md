# File Research: sources/os/plan9/9front/sys/src/cmd/ktrans/hash.c

This is a small string-keyed hash map used by `ktrans`. It stores fixed-size values inline after a private `Hnode` header in a growable contiguous allocation.

Key functions:
- `shash()` hashes C strings with a simple multiplicative hash.
- `hmapalloc()` allocates bucket storage and initializes map metadata.
- `hmaprepl()` inserts or replaces entries, optionally freeing previous keys, grows capacity by `realloc`, and links overflow nodes by index.
- `hmapupd()` updates using an existing key pointer when present.
- `_hmapget()`, `hmapget()`, `hmapkey()`, and `hmapdel()` implement lookup and deletion.
- `hmaprehash()` rebuilds with a new bucket count.
- `hmapreset()` marks filled entries empty and optionally frees keys.

The map is tailored to startup-loaded transliteration/dictionary data. Deletion/reset/rehash behavior is not robust enough for arbitrary long-lived mutation because empty nodes and overflow links are only partially normalized.
