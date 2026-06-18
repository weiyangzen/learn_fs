# sources/storage-engines/foundationdb/flow/include/flow/FileIdentifier.h

## Purpose
`FileIdentifier.h` provides compile-time traits for assigning compact file/type identifiers used by Flow serialization and composed wrapper types.

## Important APIs, Types, And Functions
Key templates are `HasFileIdentifierMember`, `CompositionDepthFor`, `FileIdentifierForBase`, `FileIdentifierFor`, `HasFileIdentifier`, `ComposedIdentifier`, and `ComposedIdentifierExternal`. `FileIdentifier` is an alias for `uint32_t`.

## Control Flow
There is no runtime control flow. Templates detect static `file_identifier` and `composition_depth` members, enforce constraints with `static_assert`, and build composed identifiers by reserving high bits for wrapper identity.

## State And Persistence Behavior
Identifiers are compile-time constants. Non-composed IDs must fit under 24 bits. Up to two wrapper-composition levels are represented in the high byte/nibbles.

## Dependencies And Integration Points
It depends on `<cstdint>` and `<type_traits>`. It integrates with object serializer traits and any type declaring `constexpr static FileIdentifier file_identifier`.

## Risks And Edge Cases
Duplicate manually assigned IDs are not detected here. Types with more than two composition levels lose composed identifiers. Wrapper ID `B` must be 1..15. Changing an identifier can break persisted data compatibility.

## Test Signals
Compile-time tests should validate detection, composition-depth limits, high-bit composition layout, absence behavior for types without identifiers, and static assertions for oversized IDs.
