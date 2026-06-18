# File Research: sources/os/bsd/openbsd-src/sbin/iked/sntrup761.sh

This shell script generates the amalgamated `sntrup761.c` source from SUPERCOP `supercop-20201130/crypto_kem/sntrup761/ref` and related sorting sources.

Key responsibilities:
- Emits OpenBSD header comments and public-domain author lines from SUPERCOP implementor metadata.
- Emits common includes and maps SUPERCOP integer type names to `crypto_api.h` names with preprocessor defines.
- Concatenates a fixed list of SUPERCOP source/header fragments.
- Applies `sed` transformations to:
  - Remove includes and externs.
  - Rename exported `crypto_kem_` symbols to `crypto_kem_sntrup761_`.
  - Make non-exported functions static.
  - Remove namespace macros and duplicate type defines.
  - Rename sort functions to `crypto_sort_int32` and `crypto_sort_uint32`.
  - Remove unused division helpers to prevent warnings.
  - Patch `int32_MINMAX` intermediate arithmetic to use `int64_t` and avoid signed 32-bit overflow when used by unsigned sorting.

Inputs and outputs:
- Expects to be run with the SUPERCOP root as `$1`.
- Writes the generated C source to stdout.

Security and correctness notes:
- The script is reproducibility-critical for auditing local modifications to the vendored cryptographic code.
- It relies on exact upstream paths and text patterns; upstream source layout changes could silently require script updates.
