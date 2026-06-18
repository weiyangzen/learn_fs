# sources/user-network-fs/samba/source3/lib/netapi/libnetapi.h

## Purpose

`libnetapi.h` declares Samba's public NetAPI C functions and the corresponding internal `_r`/`_l` implementation entry points. It was read as a complete 523-line file. The header is generated-style API glue between external callers, generated request structures, and source files implementing each API family.

## Important APIs, Types, and Functions

The header declares `NET_API_STATUS` public functions and `WERROR` internal functions for join/offline join, server/workstation, DC discovery, user, group, localgroup, time, share, file, shutdown, and netlogon-control APIs. It references important public structs through signatures, including `DOMAIN_CONTROLLER_INFO`, `domsid`, `GUID`, and many `uint8_t **buffer` NetAPI result buffers. Every operation generally has `Name(...)`, `Name_r(struct libnetapi_ctx *, struct Name *)`, and `Name_l(struct libnetapi_ctx *, struct Name *)` declarations.

## Control Flow

There is no executable control flow in the header. It defines the compile-time contract followed by `libnetapi.c` wrappers and implementation files such as `group.c`, `localgroup.c`, `file.c`, `getdc.c`, and `joindomain.c`.

## State and Persistence Behavior

The header owns no state. Its signatures define state ownership conventions: caller-provided inputs, caller-visible output pointer slots, buffers later freed through NetAPI mechanisms, and context-based internal implementations. Join, group, localgroup, file-close, share, shutdown, and similar APIs imply persistent remote or local state changes through their implementations.

## Dependencies and Integration Points

It depends on types declared before inclusion by Samba's generated NDR and security headers. It integrates the public ABI, the generated libnetapi request structs from `librpc/gen_ndr/libnetapi.h`, and all implementation modules. Header guard `__LIBNETAPI_LIBNETAPI__` prevents multiple inclusion.

## Risks and Edge Cases

Prototype mismatches here break external ABI consumers and the generated wrapper layer. Since many parameters are raw pointers with Windows-style `[in]`, `[out]`, `[unique]`, and `[ref]` comments, callers must follow the expected nullability contract even where C types cannot enforce it. Adding or removing APIs requires synchronized changes in generated NDR structs, wrappers, examples, and implementation files.

## Test Signals

Compile tests should include standalone consumers that include this header, full Samba builds with all implementation files, ABI symbol checks for public `NET_API_STATUS` functions, and wrapper/implementation prototype mismatch detection through warnings-as-errors.
