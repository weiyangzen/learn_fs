# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2Session.cs

## Purpose

Stores SMB2 authenticated session state, connected tree shares, open files keyed by volatile file id, open searches, signing metadata, and security context.

## Important APIs, Types, And Functions

Methods add/get/disconnect trees, add/get/remove open files, report open file information, manage open searches, and close the session. Properties expose session key, security context, user/machine names, creation time, signing-required flag, and signing key.

## Control Flow

Tree ids and volatile file ids are session-scoped counters. Add-open-file creates an SMB2 `FileID` with persistent equal to volatile because durable handles are unsupported. Disconnecting a tree closes matching open handles and removes the tree.

## State And Persistence Behavior

Session-local memory only. Open handles persist until close, tree disconnect, or session close; durable handle persistence across disconnect is explicitly not implemented.

## Dependencies And Integration Points

Uses `ISMBShare`, `OpenFileObject`, `OpenSearch`, `FileID`, and `SecurityContext`.

## Risks And Edge Cases

Open searches are mutated without locking. `GetConnectedTree` and `IsTreeConnected` are not locked. Persistent file ids are synthetic, so SMB2 durable/persistent handle clients will not get reconnect semantics.

## Test Signals

Test tree/file id uniqueness, invalid cross-session file id rejection, signing metadata preservation, tree disconnect cleanup, and open-search lifecycle.

Source-read signal: reviewed the complete local source file for this item.
