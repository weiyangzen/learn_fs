# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcmd5.cc

Purpose: implements the MD5 checksum calculator for XRootD using Colin Plumb's public-domain MD5 algorithm adapted into `XrdCksCalcmd5`.

Important APIs: `Init()` initializes the MD5 context constants and bit counters. `MD5Update()` accumulates bytes, processes complete 64-byte blocks, and buffers trailing data. `Final()` pads the message, appends bit length, transforms the final block, byte-reverses digest words as needed, and returns 16 digest bytes. `MD5Transform()` performs the four MD5 rounds through `MD5STEP` macros. `byteReverse()` is a no-op on little-endian and swaps words on big-endian.

Control flow: public `Update()` in the header calls `MD5Update()`. `Current()` saves and restores the context around `Final()` to inspect the digest without consuming state.

State and persistence: mutates `myContext` and `myDigest`. Persistent data is the final 16-byte checksum stored by manager/xattr code.

Dependencies: includes `XrdCksCalcmd5.hh` and platform endian support.

Risks and test signals: MD5 test vectors, segmented updates, `Current()` no-side-effect behavior, endian behavior, and repeated `Init()` reuse are key. Security-sensitive consumers should remember MD5 is not collision-resistant; here it is used as a legacy checksum, not authentication.
