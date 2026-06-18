<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpcsvc/crypt.h -->
# sources/user-network-fs/libtirpc/tirpc/rpcsvc/crypt.h

## Purpose

This rpcgen-generated libtirpc service header describes the legacy DES crypt RPC program. It defines request and response wire structures, XDR routines for the direction/mode/argument/result types, and client/server stubs for procedure `DES_CRYPT` under `CRYPT_PROG` version 1. The source was read as a complete 109-line file (2414 bytes).

## Important APIs, Types, and Functions

types: `desargs`, `desresp`, `svc_req`, `des_dir`, `des_mode` functions: `xdr_des_dir`, `xdr_des_mode`, `xdr_desargs`, `xdr_desresp` macros: `_CRYPT_H_RPCGEN`, `IXDR_GET_INT32`, `IXDR_PUT_INT32`, `IXDR_GET_U_INT32`, `IXDR_PUT_U_INT32`, `CRYPT_PROG`, `CRYPT_VERS`, `DES_CRYPT` enum values: `des_dir` (ENCRYPT_DES, DECRYPT_DES), `des_mode` (CBC_DES, ECB_DES)

## Control Flow

There is no implementation flow here; rpcgen-generated client/server code calls the declared XDR routines and `des_crypt_1` stubs, while the RPC runtime routes procedure number `DES_CRYPT` to the service implementation.

## State and Persistence Behavior

The header owns no persistent storage. State lives in caller-allocated RPC/XDR objects or generated service structures and is valid for the lifetime of the stream, request, response, or decoded allocation.

## Dependencies and Integration Points

direct includes: `rpc/rpc.h`

## Risks and Edge Cases

The service is legacy DES-oriented and generated; hand edits can desynchronize XDR declarations from implementation. Buffer lengths must be validated by the implementation because the header exposes counted variable arrays.

## Test Signals

Compile consumers that include the header from C and C++; rpcgen/XDR round-trip tests for primitive and generated structures; ABI/layout checks where supported; interoperability tests against RPC clients/servers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpcsvc/crypt.h -->
