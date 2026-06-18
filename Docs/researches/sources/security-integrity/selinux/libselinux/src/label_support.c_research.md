# sources/security-integrity/selinux/libselinux/src/label_support.c

Purpose: Provides shared label backend helpers for spec-entry parsing and digest generation.

Important APIs/types/functions: `read_spec_entries()` parses whitespace-delimited ASCII entries from a line, returning item count and optional error text. `digest_add_specfile()` appends file or mmap bytes to a digest buffer and records the path. `digest_gen_hash()` computes SHA1 over accumulated bytes.

Control flow: parsing strips trailing newline, skips blank/comment lines, rejects non-ASCII and entries at or above `UINT16_MAX`, and uses varargs to populate caller-provided `char **` outputs. Digest accumulation reallocates a growing buffer, optionally rewinds and reads a `FILE`, or copies from memory, then stores up to `DIGEST_FILES_MAX` paths.

State and persistence: digest state lives in `struct selabel_digest` attached to a label handle. `digest_gen_hash()` frees the accumulated hash buffer after finalization.

Dependencies and integration: used by file, media, X, DB, and Android backends; uses SHA1 implementation from `label_internal.h`.

Risks and test signals: parser ownership on partial failure is caller-managed. Digest overflows and max file count must be tested. Test signals include comments, unterminated final lines, non-ASCII entries, long tokens, file rewind/read failures, and mmap digest input.
