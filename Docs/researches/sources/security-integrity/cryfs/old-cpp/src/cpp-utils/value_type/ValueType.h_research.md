# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type/ValueType.h

## Purpose
Provides strongly typed value wrappers and hash/order helpers for ID-like primitive values. This specific file has 263 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `MyIdType`, `ConcreteType`, `UnderlyingType`, `IdValueType`, `must`, `std`, `hash`, `OrderedIdValueType`, `QuantityValueType`, `FlagsValueType`. Macros/constants: `MESSMER_CPPUTILS_VALUETYPE_VALUETYPE_H_`, `DEFINE_HASH_FOR_VALUE_TYPE`. Important declarations or call sites include `*     constexpr explicit MyIdType(uint32_t id): IdValueType(id) {}`; `*   DEFINE_HASH_FOR_VALUE_TYPE(MyIdType);`; `constexpr IdValueType& operator=(IdValueType&& rhs) noexcept(noexcept(*std::declval<UnderlyingType*>() = std::move(rhs.value_))) {`; `value_ = std::move(rhs.value_);`; `constexpr IdValueType& operator=(const IdValueType& rhs) noexcept(noexcept(*std::declval<UnderlyingType*>() = rhs.value_)) {`; `return operator=(IdValueType(rhs));`; `: value_(value) {`; `friend constexpr bool operator==(ConcreteType lhs, ConcreteType rhs) noexcept(noexcept(std::declval<UnderlyingType>() == std::d...`; `friend constexpr bool operator!=(ConcreteType lhs, ConcreteType rhs) noexcept(noexcept(lhs == rhs)) {`; `size_t operator()(ClassName x) const noexcept(noexcept(std::hash<ClassName::underlying_type>()(x.value_))) {   \`. CMake commands used here include `static_assert`. Primary includes/dependencies visible in the file include `functional`, `cpp-utils/assert/assert.h`.

## Control Flow
Value wrappers are inline constexpr-style operators around an underlying scalar; comparison, hashing, and accessors are generated without owning external resources.

## State and Persistence Behavior
Each value object stores only its underlying primitive value.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `functional`, `cpp-utils/assert/assert.h`.

## Risks and Edge Cases
Strong typedefs are only as safe as their constructors; exposing the underlying value can reintroduce primitive confusion.

## Test Signals
Compile/run tests should verify equality/order/hash behavior, constexpr construction, and no accidental cross-type comparison.
