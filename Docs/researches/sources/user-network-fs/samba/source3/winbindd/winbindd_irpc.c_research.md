# sources/user-network-fs/samba/source3/winbindd/winbindd_irpc.c

## Purpose
Registers and implements winbind's IRPC entry points, bridging source4-style internal messaging callers to winbind child/domain RPC operations and local async lookup helpers.

## Important APIs, Types, And Control Flow
`winbind_imessaging_context()` lazily creates an imessaging context using the global messaging server id and a loadparm context allocated on NULL to survive fork cleanup. `wb_irpc_forward_rpc_call()` forwards a generated RPC request to a domain child binding, sets the child binding timeout, marks `msg->defer_reply`, and replies in `wb_irpc_forward_callback()`. Forwarded operations include RODC DNS update, SamLogon, LogonControl, forest trust information, and SendToSam after domain routing/validation. LSA IRPC calls are implemented locally: `LookupSids3` calls `wb_lookupsids`; `LookupNames4` parses qualified names, runs parallel `wb_lookupname` calls, resolves domain SIDs, and builds LSA translated SID arrays. `wb_irpc_GetDCName()` wraps `wb_dsgetdcname`.

## State And Persistence
Keeps a static imessaging context. Individual IRPC calls allocate state under the message and send async replies. Forest trust or netlogon persistence occurs only in forwarded child server implementations.

## Dependencies And Integration Points
Uses IRPC registration macros, generated winbind/LSA/netlogon NDR types, global messaging/event contexts, domain routing helpers, wb lookup helpers, and child binding handles.

## Risks And Test Signals
Risks include missing async replies on early errors after partial subrequests, timeout mismatch, accepting only fully qualified LookupNames4 inputs, domain routing subtleties on DCs, and multiple pending name lookups racing to reply on failure. Test all registered IRPC opnums, unknown domains with authoritative flags, UPN and DOMAIN\\name parsing, partial LSA mappings, DC member vs AD DC roles, and child failure during deferred reply.
