# sources/user-network-fs/samba/source3/lib/netapi/libnetapi.c

## Purpose

`libnetapi.c` is the public C ABI wrapper layer for Samba's NetAPI implementation. It was read as a complete 3,019-line file. Every exported `NET_API_STATUS Net*` function constructs the generated request structure, obtains the singleton libnetapi context, copies input/output pointers into the structure, dispatches to the local or remote implementation, records the result, optionally emits NDR debug traces, and returns the `WERROR` value as `NET_API_STATUS`.

## Important APIs, Types, and Functions

The file exports wrappers for join/domain, server, workstation, DC discovery, user, group, localgroup, remote time, share, file, shutdown, and netlogon-control APIs. Examples in this subset include `NetGroupAdd`, `NetGroupEnum`, `NetGroupSetUsers`, `NetLocalGroupAddMembers`, `NetFileEnum`, `NetGetDCName`, `DsGetDcName`, and `NetJoinDomain`. Common helpers/macros used in almost every wrapper are `libnetapi_getctx()`, `talloc_stackframe()`, `ZERO_STRUCT`, `NDR_PRINT_IN_DEBUG`, `NDR_PRINT_OUT_DEBUG`, `LIBNETAPI_LOCAL_SERVER`, and `W_ERROR_V`.

## Control Flow

The repeated wrapper flow is: allocate a temporary talloc frame, zero the generated request struct, initialize or fetch the global context, assign input fields, assign output pointer fields, print the input request when `DEBUGLEVEL >= 10`, call either `_l` or `_r` based on local-server detection, store `r.out.result`, print the output request at debug level 10, free the frame, and return the result. Some APIs are intentionally local-only through their wrappers (`NetUserChangePassword`, ODJ provision/request/compose), while most choose local vs remote.

## State and Persistence Behavior

This file does not directly own durable state, but it is the choke point through which callers reach stateful implementations. It uses temporary talloc stack frames for wrapper-local request structs; output buffers are allocated by callees under the libnetapi context or via `NetApiBufferAllocate` and are returned through caller-provided pointers. Debug printing can expose structured request/response details at high debug levels.

## Dependencies and Integration Points

It depends on generated `librpc/gen_ndr/libnetapi.h` request/response structs, generated NDR debug printers, `libnetapi.h` prototypes, `netapi_private.h` local-server and implementation declarations, and the context lifecycle in `netapi.c`. It is the ABI entry used by example binaries, Samba's `net` command integration, and external libnetapi consumers.

## Risks and Edge Cases

Because wrappers are generated-style boilerplate, signature drift between `libnetapi.h`, generated structs, and implementation `_l/_r` functions is a primary risk. The wrappers generally do not validate null output pointers before passing them down, so each callee must enforce its own contract. At debug level 10, NDR traces may include sensitive inputs such as account names, passwords, membership data, or join blobs unless individual NDR fields suppress printing. The singleton context means process-global configuration and credentials can affect all wrapper calls.

## Test Signals

Useful tests are ABI compile/link coverage for every exported function, local-vs-remote dispatch tests using null/local/remote server names, debug-level trace smoke tests, null output pointer negative tests delegated to callees, and example binary builds from `examples/wscript_build`.
