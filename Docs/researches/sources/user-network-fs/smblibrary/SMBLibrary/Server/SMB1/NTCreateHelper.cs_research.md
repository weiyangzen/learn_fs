# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NTCreateHelper.cs

## Purpose

Implements SMB1 NT Create AndX open/create handling for files and named pipes.

## Important APIs, Types, And Functions

`GetNTCreateResponse` performs path normalization, access derivation, share access checks, `CreateFile`, session FID allocation, and response creation. Private helpers build named-pipe and filesystem basic/extended responses and map file status/attributes.

## Control Flow

The helper adds `FILE_READ_ATTRIBUTES` to desired access to query network-open information after create. If FID allocation fails, it closes the file-store handle. Named pipes return pipe resource metadata; filesystem opens return timestamps, sizes, attributes, directory flag, and maximal access masks for extended responses.

## State And Persistence Behavior

Creates persistent/open file-store handles and records them in `SMB1Session` open-file state. Actual file creation/truncation depends on requested disposition.

## Dependencies And Integration Points

Depends on SMB1 NT create command types, `NTFileStoreHelper`, `FileSystemShare`, `NamedPipeShare`, `INTFileStore`, and session security context.

## Risks And Edge Cases

Maximal access rights are hard-coded rather than computed from ACLs. Attribute conversion only keeps a subset. The extra read-attributes access can alter authorization requirements compared with the client's request.

## Test Signals

Test file create/open/overwrite statuses, directory opens, named-pipe responses, extended response rights, FID exhaustion cleanup, and access-denied behavior.

Source-read signal: reviewed the complete local source file for this item.
