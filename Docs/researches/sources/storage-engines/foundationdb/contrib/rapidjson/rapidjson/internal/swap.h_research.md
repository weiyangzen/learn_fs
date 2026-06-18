# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/swap.h

Purpose: This header defines a minimal `internal::Swap()` helper to avoid depending on `<algorithm>` for primitive swaps.

Important APIs and functions: `template <typename T> inline void Swap(T& a, T& b) RAPIDJSON_NOEXCEPT` copies `a` into a temporary, assigns `b` to `a`, then assigns the temporary to `b`.

Control flow: There is only the three-assignment swap sequence. It is intended for primitive or pointer-like types used by RapidJSON internals.

State and persistence behavior: No state beyond the two references being swapped. No persistence.

Dependencies and integration points: It includes `rapidjson.h` for namespace and `RAPIDJSON_NOEXCEPT`. `Stack::Swap()` and regex search state swapping use it.

Risks: The comment explicitly says primitive C++ types only. Using it for complex types can be slower or semantically wrong if move-aware or exception-aware swapping is needed. It does not use ADL or specialized swaps.

Test signals: Simple compile/runtime checks for primitive values and pointers, plus integration tests for `Stack::Swap()` preserving allocator and buffer state.
