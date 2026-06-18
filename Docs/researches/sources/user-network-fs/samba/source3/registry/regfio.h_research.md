<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/regfio.h -->
# sources/user-network-fs/samba/source3/registry/regfio.h

Purpose: Defines the in-memory representation and public API for Samba's Windows registry hive I/O library.

Important APIs, types, and functions: Provides constants for block sizes, record headers, value flags, NK key types, and `REGF_OFFSET_NONE`. Declares `REGF_HBIN`, `REGF_HASH_REC`, `REGF_LF_REC`, `REGF_VK_REC`, `REGF_SK_REC`, `REGF_NK_REC`, and `REGF_FILE`. Public functions are `regfio_open()`, `regfio_close()`, `regfio_rootkey()`, `regfio_fetch_subkey()`, and `regfio_write_key()`.

Control flow: No executable logic. The structures mirror hive records while also carrying runtime-only links, offsets, parse streams, dirty flags, memory contexts, fd state, and iteration indexes used by `regfio.c`.

State and persistence behavior: `REGF_FILE` is the top-level mutable state for an open hive. `REGF_HBIN` nodes cache on-disk blocks and write-back state. `REGF_NK_REC` includes child LF, VK values, and SK descriptor links, while `subkey_index` makes subkey iteration stateful on the NK object itself.

Dependencies and integration points: Includes registry parse and object headers, consumes `struct regval_ctr`, `struct regsubkey_ctr`, and `struct security_descriptor`, and is used by registry import/export or hive tooling plus tests.

Risks: Public structs expose low-level offsets and mutable internals, so callers can corrupt iterator or write state. Macros `HBIN_STORE_REF` and `HBIN_REMOVE_REF` mutate refcounts without safety checks. The API is not thread-safe for shared `REGF_FILE` or `REGF_NK_REC` objects.

Test signals: Compile ABI coverage for all consumers, structure initialization tests through `regfio_open()`, iteration tests confirming `subkey_index` semantics, and writer tests that validate the emitted hive with a fresh reader.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/regfio.h -->
