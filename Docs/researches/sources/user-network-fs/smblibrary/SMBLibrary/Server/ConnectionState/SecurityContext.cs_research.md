# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SecurityContext.cs

## Purpose

Public security context object attached to authenticated sessions and passed into file-store operations.

## Important APIs, Types, And Functions

Constructor records username, machine name, client endpoint, GSS context, and access token. Properties expose user, machine, and endpoint; `AuthenticationContext` and `AccessToken` are public fields.

## Control Flow

No internal flow. Authentication helpers build it after NTLM/GSS completion, and file stores consume it for authorization decisions.

## State And Persistence Behavior

Session-scoped identity state. It does not persist beyond session lifetime.

## Dependencies And Integration Points

Depends on GSSAPI context and `IPEndPoint`; used by SMB1/SMB2 sessions and file store helpers.

## Risks And Edge Cases

Public mutable authentication/token fields can be changed by any caller. There is no null or lifetime validation of the access token.

## Test Signals

Authentication tests should verify correct user/machine/endpoint propagation and file-store authorization receiving the expected token.

Source-read signal: reviewed the complete local source file for this item.
