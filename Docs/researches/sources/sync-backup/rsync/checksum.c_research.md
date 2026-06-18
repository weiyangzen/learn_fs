# sources/sync-backup/rsync/checksum.c

Purpose: checksum algorithm negotiation and digest computation for transfer checksums, file-list checksums, daemon auth, and generic accumulators.

Important APIs/types/functions: checksum registries `valid_checksums` and `valid_auth_checksums`; `parse_csum_name`, `parse_checksum_choice`, `csum_len_for_type`, `canonical_checksum`, `get_checksum1`, `get_checksum2`, `file_checksum`, `sum_init`, `sum_update`, `sum_end`, `init_checksum_choices`.

Control flow: initialization verifies optional OpenSSL/xxhash algorithms, negotiation picks transfer/file checksum names, digest functions dispatch among xxhash, xxh3, MD5, MD4 variants, SHA via OpenSSL, and none. File checksums map files in chunks; streaming sums keep one active accumulator.

State and persistence: globals track chosen algorithms, digest lengths, OpenSSL contexts, xxhash states, and current accumulator. No filesystem persistence except reading files for checksums.

Dependencies/integration: used by transfer matching, `--checksum`, daemon auth, batch output, and protocol negotiation.

Risks: many protocol compatibility branches preserve historical MD4 bugs and seed order. Static contexts are not reentrant. Algorithm availability varies by build.

Test signals: protocol-version tests, sanitizer/valgrind, and checksum-dependent transfer tests exercise this heavily.
