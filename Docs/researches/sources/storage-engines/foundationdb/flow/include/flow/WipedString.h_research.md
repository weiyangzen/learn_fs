# sources/storage-engines/foundationdb/flow/include/flow/WipedString.h

## Purpose
Defines `WipedString`, a sensitive-data string wrapper that stores bytes in wipe-after-use arena memory and marks serialized buffers for wiping when supported.

## Important APIs, Types, And Functions
`WipedStringSerdesWrapper` gives `StringRef` distinct serialization traits. `is_wipe_enabled` detects `markForWipe`. `dynamic_size_traits<WipedStringSerdesWrapper>` copies bytes and marks output ranges. `WipedString` provides constructors from `StringRef`, conversion/content access, and `serialize`.

## Control Flow
Construction copies bytes into an arena allocation tagged `WipeAfterUse`. Serialization wraps the internal `StringRef`; save copies bytes to the output buffer and calls wipe hooks, while load delegates to `StringRef` loading.

## State And Persistence Behavior
State is an `Arena` plus `StringRef` into wipe-enabled memory. Serialized payloads can be persisted/transmitted, but the serializer context is told to wipe temporary buffers after use.

## Dependencies And Integration Points
Depends on Flow serialization, `Arena`, file identifiers, and object serializer traits. Integrates with BinaryWriter/ObjectWriter/FlatBuffers contexts that support wiping.

## Risks And Edge Cases
Implicit `StringRef` conversion can leak bytes into non-wiping buffers. Bypassing the wrapper would use normal `StringRef` traits and lose wipe marking. The header notes deserialized `WipedString` does not arrange destruction wiping for that instance.

## Test Signals
Round trips, wipe hook invocation, keepalive allocator wipe tracking, empty-string behavior, and verifying normal `StringRef` traits are not used.
