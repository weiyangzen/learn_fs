# sources/sync-backup/rsync/lib/md5-asm-x86_64.S

Purpose: x86-64 optimized MD5 compression routine used when `USE_MD5_ASM` is enabled.

Important APIs/types/functions: exported `md5_process_asm(md_context *ctx, const void *data, size_t num)`, with Apple symbol aliasing to `_md5_process_asm`. The function expects the first four 32-bit words of `md_context` to be MD5 A/B/C/D state and processes `num` 64-byte blocks.

Control flow: under `USE_MD5_ASM`, the routine saves callee-saved registers, computes the end pointer from `num << 6`, loads A/B/C/D from the context, loops over each 64-byte block, performs all four MD5 rounds with inline constants, rotations, and message-word loads, adds the saved state to the transformed state, advances by 64 bytes, then writes A/B/C/D back and restores registers.

State and persistence behavior: mutates only the supplied digest context. It does not update bit counts or buffer state; `md5_update` in `md5.c` owns that surrounding state and calls this only for complete chunks.

Dependencies/integration: includes `config.h` and `md-defines.h`; called by `md5.c` when `USE_MD5_ASM` is set. The assembly comments state binary compatibility with OpenSSL-style MD5 context fields for the accessed words.

Risks/test signals: risks include ABI/register-save mistakes, context layout drift, endianness assumptions, and build portability across assemblers/Mach-O/Linux. Tests should compare MD5 vectors with and without `USE_MD5_ASM`, process multiple chunks and zero chunks, and run under sanitizers or ABI checkers where possible.
