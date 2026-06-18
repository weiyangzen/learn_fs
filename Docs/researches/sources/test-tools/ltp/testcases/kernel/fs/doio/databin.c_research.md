# sources/test-tools/ltp/testcases/kernel/fs/doio/databin.c

Purpose: generates and checks binary test patterns for doio filesystem stress operations.

Important APIs/types/functions: `databingen`, `databinchk`, static `Errmsg`, modes `a`, `c`, `C`, `o`, `z`, and `r`, plus optional `UNIT_TEST` main.

Control flow: generation fills buffers by mode: alternating `0x55`, checkerboard `0xf0`, counting pattern `(offset + ind) % 8`, all ones `0xff`, zeros, or random high-bit-ish bytes. Checking returns `-1` for success, the absolute failing offset for deterministic patterns, or immediately `-1` for random mode because it cannot be verified. Counting mode validates each byte against its offset-derived value; fixed modes compare every byte against one expected byte value.

State/persistence behavior: writes caller buffers and uses a static error message buffer. Random mode uses process-global `rand()` state.

Dependencies/integration: built into doio tools through `databin.h` and shared object dependencies in the Makefile.

Risks/test signals: random mode provides no integrity signal. Static `Errmsg` is not thread-safe. Signed `char` comparisons in counting mode can be platform-sensitive, though expected values are small.
