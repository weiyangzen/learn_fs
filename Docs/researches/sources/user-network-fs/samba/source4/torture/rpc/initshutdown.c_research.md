# sources/user-network-fs/samba/source4/torture/rpc/initshutdown.c

## Purpose
This file defines the `rpc.initshutdown` suite for the InitShutdown RPC interface. It tests initiating a system shutdown through both `Init` and `InitEx`, then immediately aborts the pending shutdown.

## Important APIs, Types, And Functions
`torture_rpc_initshutdown()` registers an RPC tcase on `ndr_table_initshutdown`. `init_lsa_StringLarge()` fills shutdown message strings. `test_Init()` calls `dcerpc_initshutdown_Init_r`; `test_InitEx()` calls `dcerpc_initshutdown_InitEx_r`; `test_Abort()` calls `dcerpc_initshutdown_Abort_r`.

## Control Flow
The suite contains two dangerous tests. Each allocates a message string, sets force-applications, timeout 30 seconds, and reboot true, sends the shutdown request, checks transport and WERROR success, and then calls `test_Abort()` with a null server pointer value to cancel it.

## State And Persistence Behavior
This file intentionally schedules a reboot/shutdown on the target host and relies on a follow-up abort to cancel the operation. No persistent Samba data is changed, but the system-level side effect is severe if abort fails, is delayed, or permissions allow shutdown but not abort.

## Dependencies And Integration Points
The file depends on generated InitShutdown NDR stubs and the torture RPC framework. It integrates directly with Windows-compatible remote shutdown service semantics and WERROR result handling.

## Risks And Edge Cases
Both tests are marked `dangerous` for good reason. A target may begin shutdown actions before abort completes. The message initializer only sets the string pointer, not explicit length/size fields, relying on generated marshalling semantics for `lsa_StringLarge`. Running against production hosts is unsafe.

## Test Signals
Signals are NTSTATUS success and WERR success for `Init` or `InitEx`, followed by NTSTATUS and WERR success for `Abort`.
