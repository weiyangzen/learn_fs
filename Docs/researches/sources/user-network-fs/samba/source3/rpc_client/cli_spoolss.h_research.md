# sources/user-network-fs/samba/source3/rpc_client/cli_spoolss.h research

## Purpose

`cli_spoolss.h` declares source3 convenience wrappers for the SPOOLSS RPC interface. It gives callers WERROR-returning APIs for printer open, add, query, and enumeration operations while hiding generated NDR call details.

## Important APIs, types, and functions

The header declares `rpccli_spoolss_openprinter_ex()`, `rpccli_spoolss_getprinterdriver()`, `rpccli_spoolss_getprinterdriver2()`, `rpccli_spoolss_addprinterex()`, `rpccli_spoolss_getprinter()`, `rpccli_spoolss_getjob()`, `rpccli_spoolss_enumforms()`, `rpccli_spoolss_enumprintprocessors()`, `rpccli_spoolss_enumprintprocessordatatypes()`, `rpccli_spoolss_enumports()`, `rpccli_spoolss_enummonitors()`, `rpccli_spoolss_enumjobs()`, `rpccli_spoolss_enumprinterdrivers()`, `rpccli_spoolss_enumprinters()`, `rpccli_spoolss_getprinterdata()`, `rpccli_spoolss_enumprinterkey()`, and `rpccli_spoolss_enumprinterdataex()`.

The prototypes use `struct rpc_pipe_client`, `policy_handle`, generated SPOOLSS unions, WINREG value type enum, `DATA_BLOB`-style byte outputs, and caller-provided talloc contexts.

## Control flow and contracts

All functions require an already-opened and bound `rpc_pipe_client` for the SPOOLSS interface. Query and enumeration APIs follow a caller-visible `offered` size contract but internally may retry with a server-provided `needed` size. Output arrays and information unions are allocated or filled under `mem_ctx`.

## State and persistence behavior

The header itself exposes no state. The wrappers consume `cli->binding_handle`, and some open/add operations depend on username/server-name fields populated by the bind layer. Server-side state is accessed through policy handles returned by SPOOLSS.

## Dependencies and integration points

This header is included by printer administration and RPC client code. It aligns source3 callers with generated SPOOLSS NDR structures while using WERROR as the public status type.

## Risks and test signals

The main API risks are invalid policy handles, wrong `level` values for output unions, and callers supplying too-small or zero `offered` sizes without handling retry errors. Compile tests should ensure generated SPOOLSS types remain compatible; behavioral tests should validate open, query, enum, and buffer retry contracts.
