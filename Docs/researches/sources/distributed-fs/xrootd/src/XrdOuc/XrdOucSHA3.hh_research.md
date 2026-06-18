# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSHA3.hh

Purpose: declares the public SHA3/SHAKE interface and context structure used by XRootD utility code.

Important APIs, types, and functions: `sha3_ctx_t` contains the 200-byte Keccak state as bytes or 64-bit words plus rate, digest length, cursor, and xof flag. `MDLen` enumerates byte lengths for SHA3-128/224/256/384/512. Public static methods are `Calc()`, `Init()`, `Update()`, `Final()`, `SHAKE128_Init()`, `SHAKE256_Init()`, `SHAKE_Update()`, and `SHAKE_Out()`.

Control flow: callers either use `Calc()` for a complete digest or call init/update/final manually. SHAKE users initialize with one of the SHAKE helpers, absorb with `SHAKE_Update()`, and call `SHAKE_Out()` one or more times.

State and persistence: the header exposes a POD-like context so callers can allocate it on the stack or embed it. There is no class instance state.

Dependencies and integration points: depends on `<stddef.h>` and `<cstdint>`. The implementation provides a small internal crypto primitive without requiring external crypto libraries.

Risks and test signals: exposing internal context makes ABI and layout changes visible to callers. The enum names are digest byte lengths despite comments saying bits-to-bytes. Tests should verify header/API compatibility and known-vector behavior through both one-shot and streaming paths.
