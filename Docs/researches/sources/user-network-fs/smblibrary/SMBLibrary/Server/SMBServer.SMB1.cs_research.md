<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB1.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB1.cs

## Purpose
SMB1 request dispatch for the server. It handles negotiation, session setup, tree validation, command routing, SMB1 AndX batching, response header preparation, and send-queue enqueueing.

## APIs, Types, and Functions
Key methods are `ProcessSMB1Message()`, the two `ProcessSMB1Command()` overloads, `EnqueueMessage()`, and `PrepareResponseHeader()`. It dispatches to helpers for negotiate, session setup, tree connect, file store operations, transactions, NT create, locking, read/write, cancel, and close.

## Control Flow, State, and Persistence
Before negotiation, only `NegotiateRequest` is accepted; supported NT LM 0.12 negotiation transitions the base connection to `SMB1ConnectionState` and registers it with `ConnectionManager`. After negotiation, duplicate negotiate is rejected. Most commands require a valid UID, and file/tree commands require a valid TID. Responses are batched into AndX chains when possible. State changes include session creation/removal, tree mappings, open files, searches, transaction state, and queued packets.

## Dependencies and Integration
Called from `SMBServer.ProcessPacket()` after SMB1 parsing. It depends on SMB1 command classes, protocol helper classes, `GSSProvider`, `SMBShareCollection`, `NamedPipeShare`, and NetBIOS session packet serialization.

## Risks and Test Signals
Risks include a long type-check dispatch chain, shared response header mutation across batched commands, incomplete SMB1 command coverage, and security/session cleanup correctness on logoff. Test negotiate-only enforcement, extended and non-extended session setup, invalid UID/TID, AndX batching, every routed command family, no-response NT cancel, and logoff context deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB1.cs -->
