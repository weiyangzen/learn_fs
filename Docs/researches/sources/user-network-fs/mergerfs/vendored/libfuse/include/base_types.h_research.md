<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/base_types.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/base_types.h

Purpose: This header centralizes fixed-width primitive aliases used by the vendored libfuse C and C++ headers. It maps `u16/s16/u32/s32/u64/s64` and const variants to `<stdint.h>` types, and defines `f32/f64/f80` floating aliases.

Important behavior: compile-time typedef assertions verify that `float` is 32 bits and `double` is 64 bits. The `f80` assertion is intended to ensure `long double` is at least 64 bits, but the expression checks `sizeof(f64) >= 8`; that always follows from the previous assertion and does not actually validate `f80`.

State and integration: there is no runtime state. This file is included by configuration and connection headers where short aliases make ABI structs more compact to read.

Risks and test signals: typedef names are global and can collide in broad C/C++ include contexts. The `f80` assertion typo is a low-level portability risk. A build on unusual ABIs, plus a focused compile-time static assertion for `sizeof(f80)`, would catch regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/base_types.h -->
