# sources/sync-backup/rsync/lib/mdigest.h

Purpose: common digest header for rsync's MD4 and MD5 implementations, with optional OpenSSL SHA/EVP declarations and shared context layout.

Important APIs/types/functions: includes OpenSSL `sha.h`/`evp.h` when `USE_OPENSSL` is set, includes `md-defines.h`, defines `md_context` with A/B/C/D, two 32-bit counters, and a `CSUM_CHUNK` buffer, and declares `mdfour_*` and `md5_*` functions.

Control flow: no runtime logic; compile-time inclusion changes available external digest APIs.

State and persistence behavior: `md_context` is caller-owned mutable digest state. It is transient and not directly persisted, but its layout must match C and assembly code.

Dependencies/integration: consumed by checksum and digest implementation files. The context layout is relied on by `md5-asm-x86_64.S`, so field ordering is an ABI within the source tree.

Risks/test signals: changing `md_context` layout can break assembly. OpenSSL include availability must match configure defines. Build tests should cover `USE_OPENSSL` on/off and `USE_MD5_ASM` on/off, with digest-vector tests proving layout compatibility.
