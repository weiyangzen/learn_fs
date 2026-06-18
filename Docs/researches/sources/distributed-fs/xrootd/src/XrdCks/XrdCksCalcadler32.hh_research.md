# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcadler32.hh

Purpose: implements the built-in Adler-32 checksum calculator as a header-only `XrdCksCalc` subclass.

Important APIs: `Init()` sets sum1 to 1 and sum2 to 0. `Update()` processes the buffer in chunks up to `AdlerNMax`, using unrolled `DO1/DO2/DO4/DO8/DO16` macros and modulo `AdlerBase`. `Final()` combines sums into a 32-bit value and converts to network order on little-endian platforms. `Type()` returns `"adler32"` and a 4-byte size; `New()` clones the calculator type.

Control flow and integration: managers can instantiate the calculator directly or through the loader's built-in registry. The returned binary checksum can be stored in `XrdCksData`.

State and persistence: mutable state is `unSum1`, `unSum2`, and `AdlerValue`. No persistence beyond final checksum bytes.

Dependencies: includes `XrdCksCalc.hh`, endian/platform headers, and networking byte-order support.

Risks and test signals: test vectors should compare one-shot and segmented updates, empty buffer behavior, endian output, and large buffers crossing `AdlerNMax`.
