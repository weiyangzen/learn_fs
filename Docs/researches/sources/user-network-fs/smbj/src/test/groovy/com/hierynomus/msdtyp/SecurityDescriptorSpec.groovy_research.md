# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdtyp/SecurityDescriptorSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdtyp/SecurityDescriptorSpec.groovy

Purpose: validates binary Windows security descriptor decode/encode. Important APIs/types are `SecurityDescriptor.read`, `SecurityDescriptor.write`, `SID.fromString`, `ACL`, `AceTypes.accessDeniedAce`, `AceTypes.accessAllowedAce`, `AccessMask`, `AceFlags`, `AceType`, and `SecurityDescriptor.Control`. Control flow decodes a fixed hex descriptor, checks owner/group SIDs, DACL revision, six ACEs, masks, inherited flags, padding handling, and null SACL, then builds an equivalent descriptor and asserts exact serialized bytes.

State and persistence: transient buffers only. Dependencies are SMB buffer utilities and MS-DTYP SID/ACL/ACE models. Integration risk is high because descriptor layout uses offsets, variable SID lengths, ACE padding, and endian-sensitive masks. Test signal is strong for a realistic DACL round trip, but it covers only these ACE classes and one control flag combination.
