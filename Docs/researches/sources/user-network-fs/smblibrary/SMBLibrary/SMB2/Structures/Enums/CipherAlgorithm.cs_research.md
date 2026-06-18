# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/CipherAlgorithm.cs

## Purpose

Declares SMB 3.1.1 negotiate encryption cipher identifiers: AES-128-CCM, AES-128-GCM, AES-256-CCM, and AES-256-GCM.

## Important APIs, Types, And Functions

The public `CipherAlgorithm : ushort` enum maps wire values `0x0001` through `0x0004`.

## Control Flow

There is no control flow; values are consumed by encryption capability parsing and negotiate selection.

## State And Persistence Behavior

No runtime state. The selected enum value becomes part of negotiated session encryption state elsewhere.

## Dependencies And Integration Points

Used by `EncryptionCapabilities` and SMB2 negotiate/encryption code.

## Risks And Edge Cases

Compatibility depends on negotiate code respecting dialect support. Advertising AES-256 ciphers to dialects or peers that do not support them would be a higher-layer bug.

## Test Signals

Verify wire-value round trips and cipher ordering preference in negotiate capability tests.

Source-read signal: reviewed the complete local source file for this item.
