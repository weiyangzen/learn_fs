# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/meta.h

Purpose: This header provides lightweight compile-time type traits and SFINAE helpers for RapidJSON without requiring C++11 `<type_traits>` by default.

Important APIs and types: It defines `Void`, `BoolType`, `TrueType`, `FalseType`, `SelectIf`, `BoolExpr`, `NotExpr`, `AndExpr`, `OrExpr`, `AddConst`, `MaybeAddConst`, `RemoveConst`, `IsSame`, `IsConst`, `IsMoreConst`, `IsPointer`, `IsBaseOf`, `EnableIf`, and `DisableIf`. Macros `RAPIDJSON_ENABLEIF`, `RAPIDJSON_DISABLEIF`, `RAPIDJSON_ENABLEIF_RETURN`, and `RAPIDJSON_DISABLEIF_RETURN` wrap the internal SFINAE machinery.

Control flow: There is no runtime flow. Template specialization and enum `Value` constants drive overload selection, const-correct iterator conversions, pointer/value overload disambiguation, and optional use of `std::is_base_of` when `RAPIDJSON_HAS_CXX11_TYPETRAITS` is enabled.

State and persistence behavior: No runtime state or persistence. The file is pure compile-time infrastructure.

Dependencies and integration points: It includes `rapidjson.h` and optionally `<type_traits>`. `document.h`, `pointer.h`, and related DOM APIs use these traits to constrain constructors and overloads.

Risks: The custom `IsBaseOf` implementation is a simplified Boost-style trait and can behave differently from full standard traits for exotic incomplete/private cases. The macros are subtle; misuse can yield difficult template errors. `NULL` appears in SFINAE defaults, so macro contexts must stay compatible with C++03.

Test signals: Compile tests should verify overload selection for pointer versus value types, const-to-nonconst conversion rejection, base-class detection with and without `<type_traits>`, and custom namespace qualification in SFINAE macros.
