# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/msinttypes/inttypes.h

Purpose: This compatibility header supplies C99-style `inttypes.h` definitions for older Microsoft Visual C++ compilers that lack complete support.

Important APIs and types: It includes local `stdint.h`, defines `imaxdiv_t`, `PRI*` and `SCN*` format macros for signed/unsigned exact, least, fast, max, and pointer-width integers, and maps `imaxabs`, `imaxdiv`, `strtoimax`, `strtoumax`, `wcstoimax`, and `wcstoumax` to MSVC CRT equivalents. For MSVC 2013 and newer it delegates to system `<inttypes.h>`.

Control flow: Preprocessor guards reject non-MSVC compilers. `_MSC_VER >= 1800` uses the platform header. Older branches define macros conditionally based on C++ format macro rules. The inline `imaxdiv()` computes quotient and remainder and adjusts for negative numerators with positive remainders.

State and persistence behavior: No runtime state except local variables in `imaxdiv()`. The header affects compile-time macro namespace.

Dependencies and integration points: `rapidjson.h` includes this on old MSVC when RapidJSON supplies 64-bit integer support. It pairs with `msinttypes/stdint.h`.

Risks: Format macros are compiler/CRT-specific and easy to break across MSVC versions or architectures. The header intentionally errors outside MSVC. Macro collisions with Boost or system headers are mitigated but still possible.

Test signals: Compile on representative old MSVC versions, verify format/scanning macros for 32/64-bit and pointer widths, test `imaxdiv()` sign behavior, and ensure MSVC 2013+ delegates cleanly.
