# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/rapidjson.h

Purpose: This is RapidJSON's central configuration and common-definition header. It establishes version macros, namespace customization, platform detection, integer/size types, assertion/static assertion utilities, compiler diagnostic macros, C++11 feature flags, allocation customization hooks, and the JSON `Type` enum.

Important APIs and macros: Public configuration includes `RAPIDJSON_MAJOR_VERSION`, `RAPIDJSON_MINOR_VERSION`, `RAPIDJSON_PATCH_VERSION`, `RAPIDJSON_VERSION_STRING`, `RAPIDJSON_NAMESPACE`, `RAPIDJSON_HAS_STDSTRING`, `RAPIDJSON_NO_INT64DEFINE`, `RAPIDJSON_FORCEINLINE`, `RAPIDJSON_ENDIAN`, `RAPIDJSON_64BIT`, `RAPIDJSON_ALIGN`, `RAPIDJSON_UINT64_C2`, `RAPIDJSON_48BITPOINTER_OPTIMIZATION`, `RAPIDJSON_SIMD`, `RAPIDJSON_NO_SIZETYPEDEFINE`, `RAPIDJSON_ASSERT`, `RAPIDJSON_STATIC_ASSERT`, `RAPIDJSON_LIKELY`, `RAPIDJSON_UNLIKELY`, `RAPIDJSON_NOEXCEPT`, `RAPIDJSON_NEW`, and `RAPIDJSON_DELETE`. It defines `SizeType` by default and enum `Type` values for all JSON kinds.

Control flow: Most behavior is preprocessor selection. It detects endian via compiler/libc/architecture macros, selects 64-bit alignment, enables lower-48-bit pointer packing on x86-64, defines SIMD availability when requested, imports C99 integer headers or MSVC compatibility headers, and maps compiler-specific diagnostic and feature macros.

State and persistence behavior: No runtime state. Compile-time macro state controls ABI, object layout, enabled overloads, and assertions across all RapidJSON headers.

Dependencies and integration points: Every RapidJSON header depends on this file directly or indirectly. FoundationDB's vendored copy inherits these compile-time decisions wherever RapidJSON is included.

Risks: Inconsistent macro definitions across translation units can create ODR and ABI problems. Endianness detection has hard errors for unknown platforms. The 48-bit pointer optimization assumes x86-64 virtual address layout. Default `SizeType` is 32-bit even on 64-bit systems unless overridden.

Test signals: Compile with custom namespace, custom `SizeType`, std::string enabled/disabled, old MSVC integer support, endian overrides, assertions/static assertions, 32-bit and 64-bit builds, pointer optimization toggles, and writer/document behavior under custom allocation macros.
