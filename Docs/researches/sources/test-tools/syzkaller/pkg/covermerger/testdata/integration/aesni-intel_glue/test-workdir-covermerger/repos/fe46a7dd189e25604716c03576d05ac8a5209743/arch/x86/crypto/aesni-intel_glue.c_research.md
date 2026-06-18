# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/fe46a7dd189e25604716c03576d05ac8a5209743/arch/x86/crypto/aesni-intel_glue.c

This file is another AES-NI kernel-driver snapshot in the covermerger integration corpus. Its contents match the `9fe30842...` snapshot in this work item, so its purpose is to provide a second repository identity with the same source body for merge/deduplication behavior in the integration scenario.

The code registers AES cipher, block modes, xctr, and GCM/RFC4106 AEAD implementations through Linux crypto APIs. Important context structs and callbacks are the same as the matching snapshot: AES and XTS contexts, aligned GCM context buffers, key setup helpers, skcipher mode callbacks, AEAD authentication helpers, algorithm descriptor arrays, and `aesni_init`/`aesni_exit`.

Control flow is crypto-framework callback driven. Module initialization gates on AES CPU support, chooses AVX or SSE GCM paths via static branches, optionally updates CTR dispatch to an AVX-by8 helper, then registers algorithm families. Runtime requests traverse skcipher or AEAD scatter-gather walkers, enter FPU sections for assembly acceleration, and write outputs, IVs, tags, or result buffers according to mode semantics.

State is stored in transform contexts, request-local buffers, IVs, global static branch/static-call state, and SIMD registration pointers. There is no application persistence. As a fixture, persistence is the source path and repository commit directory, which lets covermerger reason about identical files across distinct repositories.

Risks are those typical of low-level crypto glue: assembly ABI drift, invalid key handling, partial-block CTS/XTS semantics, scatterlist page boundaries, AEAD authentication failure handling, and registration unwind correctness. Test signals are indirect: identical content across two commit directories is useful for detecting whether the merger keys by path/content/repository identity correctly.
