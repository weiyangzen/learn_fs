# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/value_type/ValueTypeTest.cpp

Purpose: Tests macro/template-generated value types for IDs, ordered IDs, quantities, and flags. It validates strong typing, constexpr behavior, comparisons, hashing/containers, arithmetic, and flag operations.

Important APIs and types: Defines local types such as `MyIdValueType`, `MyOrderedIdValueType`, `MyQuantityValueType`, and `MyFlagsValueType` using `ValueType.h`. Uses GoogleTest plus `set` and `unordered_set`.

Control flow: Typed test suites and static/constexpr checks instantiate value wrappers, compare values, insert them into containers, and exercise operations allowed by each category.

State and persistence behavior: All state is in-memory wrapped primitive values. No persistence.

Dependencies and integration points: Strong value types prevent accidental mixing of IDs, sizes, and flags across CryFS APIs.

Risks: Macros can produce broad API surfaces; tests must ensure unwanted operations are unavailable as well as wanted operations working. Compile-time-only failures are not always visible as runtime tests.

Test signals: Correct equality/order/hash behavior, constexpr construction, arithmetic for quantities, bitwise flag semantics, and container compatibility.
