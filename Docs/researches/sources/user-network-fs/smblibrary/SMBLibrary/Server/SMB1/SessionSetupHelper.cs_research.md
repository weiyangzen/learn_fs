# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SessionSetupHelper.cs

## Purpose

Handles SMB1 session setup for classic NTLM challenge/response and extended-security GSS/NTLM blobs.

## Important APIs, Types, And Functions

`GetSessionSetupResponse` authenticates classic `SessionSetupAndXRequest`; `GetSessionSetupResponseExtended` accepts security blobs and supports multi-step authentication; `CreateAuthenticateMessage` builds an NTLM authenticate message from legacy password fields.

## Control Flow

Classic setup constructs an authenticate message, calls `NTLMAuthenticate`, fetches session attributes, truncates session key to 16 bytes, creates a normal or guest session, sets UID, and records large read/write capabilities. Extended setup calls `AcceptSecurityContext`, allocates a UID even for more-processing-required, and creates the session on final success.

## State And Persistence Behavior

Mutates connection authentication context, creates `SMB1Session` entries, sets connection large-read/write flags, and stores session key/access token in session security context.

## Dependencies And Integration Points

Depends on `GSSProvider`, NTLM message utilities, SMB1 session setup structures, and `SMB1ConnectionState`.

## Risks And Edge Cases

The code assumes authentication context attributes are present when logging failures. UID allocation during extended multi-step auth can reserve ids before success. Guest fallback depends on provider attributes.

## Test Signals

Test classic success/failure, guest login, extended continue and final success, session key truncation, large read/write flags, UID exhaustion, and malformed password/blob inputs.

Source-read signal: reviewed the complete local source file for this item.
