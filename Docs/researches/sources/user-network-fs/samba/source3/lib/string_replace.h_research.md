## sources/user-network-fs/samba/source3/lib/string_replace.h

Purpose: public declaration for the filename character replacement mapping subsystem. It hides `struct char_mappings` and exposes initialization and application functions to VFS modules and filename translation code.

Important APIs are `string_replace_init_map`, which returns a talloc-owned sparse map array from configuration strings, `string_replace_allocate`, which maps a supplied name into a newly allocated output string, and `macos_string_replace_map`, the built-in mapping list for macOS-problematic characters.

Control flow contract: callers create or receive a mapping table once, then pass it with a direction enum to map names as they cross Unix/Windows boundaries. The output is allocated under the caller-provided `mem_ctx`; the integer return is `0` on success or an `errno` value on conversion/allocation failure.

State and persistence: no header-level storage beyond the extern map constant. Ownership of mapping tables and mapped names is talloc-based. Dependencies include `TALLOC_CTX`, `connection_struct`, and `enum vfs_translate_direction`, so consumers must include Samba connection/VFS context before using the API.

Risks and tests: because the map type is opaque, callers cannot validate internals and must rely on `string_replace_init_map` succeeding. The API allows `cmaps == NULL` for identity conversion in the implementation, so callers should test that no-map behavior still returns a converted copy. Test signals include macOS map round trips and propagation of malformed configuration entries.
