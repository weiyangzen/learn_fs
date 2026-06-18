# sources/sync-backup/rsync/lib/md-defines.h

Purpose: central digest constants shared by C and assembly digest code.

Important APIs/types/functions: digest lengths `MD4_DIGEST_LEN`, `MD5_DIGEST_LEN`, `MAX_DIGEST_LEN`; block size `CSUM_CHUNK`; checksum algorithm IDs `CSUM_gone`, `CSUM_NONE`, `CSUM_MD4_ARCHAIC`, `CSUM_MD4_BUSTED`, `CSUM_MD4_OLD`, `CSUM_MD4`, `CSUM_MD5`, `CSUM_XXH64`, `CSUM_XXH3_64`, `CSUM_XXH3_128`, `CSUM_SHA1`, `CSUM_SHA256`, and `CSUM_SHA512`.

Control flow: preprocessor logic optionally undefines SHA digest lengths when disabled and chooses `MAX_DIGEST_LEN` from the strongest available configured digest length, falling back to MD5.

State and persistence behavior: no runtime state. Algorithm IDs are part of protocol/configuration semantics and must remain stable.

Dependencies/integration: included by `mdigest.h`, `md5.c`, and `md5-asm-x86_64.S`; also aligns with checksum negotiation code elsewhere in rsync.

Risks/test signals: changing IDs or digest sizes can break wire compatibility and buffer sizing. Build tests should cover OpenSSL/no-OpenSSL configurations, disabled SHA macros, and the assembly requirement that `CSUM_CHUNK == 64`.
