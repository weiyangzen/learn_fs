<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p_types.h -->
# sources/user-network-fs/nfs-ganesha/src/include/9p_types.h

## Purpose
`9p_types.h` defines short unsigned integer aliases used by the 9P protocol code. It avoids problematic typedef redefinitions by using preprocessor aliases for fixed-width integer types.

## Important APIs, types, and functions
- `u8`, `u16`, `u32`, and `u64` are defined as macros mapping to `uint8_t`, `uint16_t`, `uint32_t`, and `uint64_t`.
- A disabled `#if 0` block documents the avoided typedef form.

## Control flow
There is no runtime control flow. Inclusion of the header makes the aliases available to `9p.h` and protocol implementation files.

## State and persistence
The header has no state. Its only effect is compile-time type spelling.

## Dependencies and integration points
The aliases require `stdint.h` to have been included before or by the includer; `9p.h` includes `<stdint.h>` before this header. The aliases are used heavily in 9P wire-structure constants, fields, and serialization macros.

## Risks
- Macro type aliases can collide with other headers or produce surprising diagnostics compared with typedefs.
- Because this header does not include `<stdint.h>` itself, standalone inclusion depends on include order.
- The copyright line includes an unusual character in the comment; it is harmless to compilation but can affect encoding-sensitive tools.

## Test signals
- Compile 9P code with strict warnings on all supported platforms.
- Include-order tests should verify no source includes `9p_types.h` before fixed-width integer types are defined, or the header should be adjusted if needed.
- Portability checks should compile with headers that already define `u8`-style aliases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p_types.h -->
