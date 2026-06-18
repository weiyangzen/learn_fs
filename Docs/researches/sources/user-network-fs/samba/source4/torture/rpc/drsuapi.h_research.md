# sources/user-network-fs/samba/source4/torture/rpc/drsuapi.h

## Purpose
`drsuapi.h` is the shared local header for the DRSUAPI torture tests. It defines fixture-private state structures for normal and W2K8-style DRS tests and wraps common DRSUAPI assertion behavior.

## Important APIs, types, and functions
`struct DsPrivate` carries admin credentials, DRS pipe, bind handle, `drsuapi_DsBindInfo28`, domain DN/GUID/DNS state, `drsuapi_DsGetDCInfo2`, a domain join handle, and DC credentials. `struct DsPrivate_w2k8` is similar but stores a bind GUID, generic `drsuapi_DsBindInfoCtr`, and `drsuapi_DsGetDCInfo3` for level 3 DC info. The macros `torture_drsuapi_assert_call_werr` and `torture_drsuapi_assert_call` convert DCERPC NTSTATUS plus request `out.result` into concise torture failures.

## Control flow
The header has no runtime control flow of its own. Including C files allocate one of the private structs in fixture setup, fill it through domain join and `DsBind`, then pass it as tcase data to individual tests. The assertion macro first checks transport status, formats an NT error on failure, and then checks the expected WERROR in the request result.

## State and persistence behavior
The structs hold borrowed and talloc-owned pointers to credentials, pipes, names, GUIDs, and join handles. They do not persist state outside a test process, but the join handles refer to domain accounts created by setup code in the C files. The macros do not clean up; they can abort a test before caller cleanup if used after a state mutation.

## Dependencies and integration points
The header includes generated `librpc/gen_ndr/drsuapi.h` and assumes consumers have visible definitions for `struct cli_credentials`, `struct dcerpc_pipe`, `struct policy_handle`, `struct test_join`, and torture assertion helpers. It is included by the DRSUAPI test modules and is the contract that lets `drsuapi.c`, `drsuapi_cracknames.c`, `drsuapi_w2k8.c`, and `dsgetinfo.c` share fixture semantics.

## Risks and edge cases
The assertion macro body references `tctx` in the `torture_fail()` call instead of consistently using the `_tctx` parameter, so it relies on callers having a variable named `tctx` in scope. Because the macros evaluate `(_pr)->out.result`, they require request structures with that member shape. Abort-on-failure can bypass caller-side best-effort cleanup if used after a mutation.

## Test signals
The macros define the canonical DRSUAPI test signal: successful RPC transport and expected request-level WERROR. `torture_drsuapi_assert_call` is the all-OK shortcut; `torture_drsuapi_assert_call_werr` captures expected failures such as duplicate or missing replica refs.
