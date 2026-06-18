# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/msinttypes/stdint.h

Purpose: This compatibility header supplies C99-style fixed-width integer types, limits, and constants for Microsoft Visual C++ compilers.

Important APIs and types: It defines exact-width, least-width, fast-width, pointer-width, and max-width integer typedefs such as `int8_t`, `uint64_t`, `intptr_t`, and `uintmax_t`; limit macros such as `INT32_MAX`, `UINT64_MAX`, `SIZE_MAX`; and constant macros such as `INT64_C` and `UINTMAX_C`. For MSVC 2010+ it includes system `<stdint.h>` but overrides integer constant macros to avoid warnings.

Control flow: Preprocessor guards reject non-MSVC compilers. Compiler-version branches either delegate to system support or define types manually. Architecture branches distinguish `_WIN64` pointer and size limits from 32-bit builds.

State and persistence behavior: There is no runtime state. The header mutates the compile-time macro/type namespace.

Dependencies and integration points: `rapidjson.h` includes it for `_MSC_VER < 1800` when RapidJSON needs global `int64_t`/`uint64_t`. `msinttypes/inttypes.h` depends on it.

Risks: This is legacy toolchain compatibility code. Incorrect `_MSC_VER`, `_WIN64`, or `_M_ARM` handling can break builds. The file deliberately wraps `<wchar.h>` linkage for older environments, which is fragile. Macro definitions can collide with other portability headers.

Test signals: Compile with supported MSVC versions and architectures, verify sizes and signedness of typedefs, constants for min/max values, `_W64` pointer types on 32-bit, and coexistence with Boost/system integer headers.
