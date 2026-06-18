# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/OpenAndXHelper.cs

## Purpose

Implements legacy SMB1 Open AndX handling and maps OpenAndX modes to NT create semantics.

## Important APIs, Types, And Functions

`GetOpenAndXResponse` normalizes path, converts access/share/open/create options, performs access checks, opens through `CreateFile`, allocates FID, and returns basic or extended file/named-pipe responses. Private converters map access mode, sharing mode, open mode, create options, and open result.

## Control Flow

Invalid access/share/open combinations become `STATUS_OS2_INVALID_ACCESS`. Successful opens add session open-file state. Named-pipe responses use pipe metadata; filesystem responses use `FileNetworkOpenInformation` and clamp file size to 32 bits.

## State And Persistence Behavior

Creates or opens file-store handles and records session FIDs. File creation/truncation follows converted disposition.

## Dependencies And Integration Points

Depends on SMB1 OpenAndX command types, shares, `NTFileStoreHelper`, and file-store create/query APIs.

## Risks And Edge Cases

`SharingMode.Compatibility` maps to read sharing only and may not match all legacy behavior. Access rights in responses are simplified. Extended maximal access rights are hard-coded.

## Test Signals

Test all access/share/open-mode conversions, invalid combinations, named-pipe open, file size clamping, FID exhaustion cleanup, and access-denied cases.

Source-read signal: reviewed the complete local source file for this item.
