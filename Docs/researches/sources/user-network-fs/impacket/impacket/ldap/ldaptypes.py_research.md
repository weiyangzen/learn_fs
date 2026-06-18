# sources/user-network-fs/impacket/impacket/ldap/ldaptypes.py

## Purpose

`ldaptypes.py` implements binary LDAP/Active Directory security data structures using Impacket's `Structure` framework. It focuses on non-RPC, self-relative NT security descriptors, SIDs, ACLs, ACE headers, ACE bodies, access masks, common object class GUID mappings, and the LDAP server SD flags enum. This module is the bridge between LDAP attributes such as `nTSecurityDescriptor` or `msDS-AllowedToActOnBehalfOfOtherIdentity` and editable Python objects that can be serialized back to the exact binary format expected by Active Directory and Windows authorization APIs.

## Important APIs, types, and constants

- `RECALC_ACE_SIZE` controls whether `ACE.getData()` recalculates ACE sizes. It defaults to `True`; tests may set it to `False` to preserve redundant null padding from Windows.
- `LDAP_SID_IDENTIFIER_AUTHORITY` wraps the 6-byte SID identifier authority.
- `LDAP_SID` parses and serializes LDAP-format SIDs. `formatCanonical()` returns `S-...` strings, and `fromCanonical()` populates binary fields from canonical SID text.
- `SR_SECURITY_DESCRIPTOR` parses and serializes self-relative security descriptors with revision/control/offset header plus optional SACL, DACL, owner SID, and group SID.
- `ACE` parses the common ACE header (`AceType`, `AceFlags`, `AceSize`) and dispatches the body to `ACE_TYPE_MAP`.
- `ACCESS_MASK` wraps a 32-bit mask and defines generic/standard rights constants plus `hasPriv()`, `setPriv()`, and `removePriv()`.
- ACE body classes cover access allowed/denied, object ACEs, callback ACEs, audit ACEs, mandatory label ACEs, resource attribute ACEs, and scoped policy ID ACEs. Important classes include `ACCESS_ALLOWED_ACE`, `ACCESS_DENIED_ACE`, `ACCESS_ALLOWED_OBJECT_ACE`, `ACCESS_DENIED_OBJECT_ACE`, `ACCESS_ALLOWED_CALLBACK_ACE`, `ACCESS_DENIED_CALLBACK_ACE`, `ACCESS_ALLOWED_CALLBACK_OBJECT_ACE`, `ACCESS_DENIED_CALLBACK_OBJECT_ACE`, `SYSTEM_AUDIT_ACE`, `SYSTEM_AUDIT_OBJECT_ACE`, `SYSTEM_AUDIT_CALLBACK_ACE`, `SYSTEM_MANDATORY_LABEL_ACE`, `SYSTEM_AUDIT_CALLBACK_OBJECT_ACE`, `SYSTEM_RESOURCE_ATTRIBUTE_ACE`, and `SYSTEM_SCOPED_POLICY_ID_ACE`.
- `ACCESS_ALLOWED_OBJECT_ACE` defines AD DS rights constants such as `ADS_RIGHT_DS_CONTROL_ACCESS`, `ADS_RIGHT_DS_CREATE_CHILD`, `ADS_RIGHT_DS_DELETE_CHILD`, `ADS_RIGHT_DS_READ_PROP`, `ADS_RIGHT_DS_WRITE_PROP`, and `ADS_RIGHT_DS_SELF`, plus object GUID presence flags.
- `ACE_TYPES` and `ACE_TYPE_MAP` are the dispatch registry from ACE type number to body class.
- `ACL` parses an ACL header and a counted list of ACE objects, exposes parsed ACEs through `self.aces` and `self['Data']`, and serializes them back with recalculated ACL size.
- `OBJECTTYPE_GUID_MAP` maps common AD object class LDAP display names (`group`, `domain`, `organizationalUnit`, `user`, `groupPolicyContainer`) to schema GUIDs.
- `LDAP_SERVER_SD_FLAGS` enumerates server-side security descriptor selection bits: owner, group, DACL, and SACL.

## Control flow and behavior

Parsing and serialization are mostly driven by `Structure` declarations with a few important overrides:

- `LDAP_SID.formatCanonical()` renders the revision, the last byte of the identifier authority, and each little-endian subauthority. `fromCanonical()` reverses the process and constructs the 6-byte authority as five zero bytes plus a one-byte authority value.
- `SR_SECURITY_DESCRIPTOR.fromString()` first parses the fixed 20-byte self-relative header through `Structure.fromString()`, then checks each offset. Nonzero owner/group offsets create `LDAP_SID` objects from the corresponding slice; nonzero SACL/DACL offsets create `ACL` objects; zero offsets store `b''`.
- `SR_SECURITY_DESCRIPTOR.getData()` rebuilds offsets in the order SACL, DACL, owner SID, group SID after the 20-byte header, using each nested object's `getData()` length, then delegates to `Structure.getData()`.
- `ACE.fromString()` parses the ACE header, looks up the body parser in `ACE_TYPE_MAP` by `AceType`, stores the class name in `TypeName`, and replaces raw `Ace` bytes with the parsed ACE body object.
- `ACE.getData()` sets or preserves `AceSize` depending on `RECALC_ACE_SIZE`, aligns size to a 4-byte boundary, serializes the header/body, and pads with null bytes if the serialized body is shorter than the stored size.
- `ACCESS_ALLOWED_OBJECT_ACE.checkObjectType()` and `checkInheritedObjectType()` drive optional 16-byte GUID field lengths from the flags. `getData()` sets the relevant presence flags when `ObjectType` or `InheritedObjectType` is non-empty before serializing.
- Callback and audit object ACE classes reuse the same object ACE layout and add trailing `ApplicationData` where required.
- `ACL.fromString()` parses the ACL header, then repeatedly parses ACEs from the remaining `Data` buffer according to `AceCount`, advancing by each ACE's `AceSize`. It raises if the header advertises more ACEs after data is exhausted.
- `ACL.getData()` sets `AceCount`, temporarily replaces `Data` with concatenated ACE bytes for parent serialization, recalculates `AclSize`, then restores `Data` to the ACE list.

## State and persistence behavior

The module has no external persistence. Its state is binary structure fields, parsed child objects, and one global behavior flag:

- `RECALC_ACE_SIZE` is mutable module-level state that changes serialization globally. It matters for byte-exact round-trips versus compact rewritten descriptors.
- `ACL` maintains parsed ACEs in `self.aces` and mirrors them in `self['Data']` after parsing. Callers often mutate `acl.aces` or `sd['Dacl']['Data']`; serialization uses `self.aces`.
- `SR_SECURITY_DESCRIPTOR.getData()` mutates offset fields each time it serializes, so the object records its last serialized layout.
- ACE object serialization may mutate `AceSize` and object ACE `Flags`, so re-encoding can normalize or alter field values even when the logical ACL is unchanged.
- Parsed nested structures preserve enough state to rebuild descriptors but do not preserve all original byte-level quirks unless `RECALC_ACE_SIZE` is disabled and padding lengths remain represented by `AceSize`.

## Dependencies and integration points

- Depends on Python `struct.unpack` / `pack`, `enum.Enum`, and Impacket `impacket.structure.Structure`.
- Consumed by LDAP attack/admin examples (`dacledit.py`, `owneredit.py`, `rbcd.py`, `badsuccessor.py`, `ldap_shell.py`, ntlmrelayx LDAP attacks) to parse existing descriptors, add/remove ACEs, set owners, and write modified descriptors back over LDAP.
- Used by `impacket/dpapi_ng.py` to construct descriptors for DPAPI-NG access control.
- Used by DCE/RPC and Kerberos-related code/tests for SID formatting and security descriptor construction, including `impacket/dcerpc/v5/nspi.py`, `impacket/krb5/pac.py`, and `tests/dcerpc/test_raa.py`.
- Complements `ldapasn1.py` and `ldap.py`: LDAP controls request specific descriptor sections, LDAP search returns raw descriptor attributes, and this module parses or builds the binary payload.

## Risks and edge cases

- `SR_SECURITY_DESCRIPTOR.fromString()` has a likely typo in the zero-DACL branch: when `OffsetDacl == 0`, it assigns `self['Sacl'] = b''` instead of `self['Dacl'] = b''`. Objects with no DACL can retain an incorrect/missing DACL field.
- `ACE.fromString()` directly indexes `ACE_TYPE_MAP[self['AceType']]`. Unknown or newer ACE types raise `KeyError` instead of preserving opaque ACE bytes, which can break parsing descriptors containing unsupported ACE types.
- `ACE.getData()` pads with `'\x00'` as a text string, not `b'\x00'`. In Python 3 this can cause type errors when padding is needed.
- The alignment adjustment uses `self['AceSize'] += self['AceSize'] % 4`; conventional 4-byte alignment should add `4 - remainder` when the remainder is nonzero. The current logic over-aligns sizes with remainder 1 or 3 and leaves remainder 2 still misaligned.
- `ACCESS_MASK.removePriv()` uses XOR. Calling it for a privilege that is not set will set that bit; a safer removal operation would use `&= ~priv`.
- `LDAP_SID.formatCanonical()` and `fromCanonical()` only handle one-byte identifier authority values. Full SID authorities are 48-bit big-endian values, so authorities larger than 255 are not represented correctly.
- `SR_SECURITY_DESCRIPTOR.getData()` always serializes in SACL, DACL, owner, group order, which may differ from the original binary order. That is valid for self-relative descriptors but can defeat byte-exact comparisons unless tests account for it.
- Object GUID fields are raw 16-byte values. Callers must handle Windows GUID byte order themselves; the module does not expose GUID parsing or string conversion helpers.
- `ACL.getData()` assumes `self.aces` exists. Manually constructed ACLs must set `aces` before serialization, as examples do.
- Several ACE body classes are documented as TODO or simplified, especially resource attribute application data and scoped policy validation. The module can preserve bytes but does not semantically parse or validate those substructures.

## Test signals

- `tests/SMB_RPC/test_ldap.py::test_security_descriptor` fetches `nTSecurityDescriptor` over LDAP, sets `impacket.ldap.ldaptypes.RECALC_ACL_SIZE = False`, parses with `SR_SECURITY_DESCRIPTOR`, and asserts byte-for-byte equality with `getData()`.
- `tests/dcerpc/test_raa.py` builds a minimal self-relative descriptor with `SR_SECURITY_DESCRIPTOR`, `LDAP_SID`, `ACL`, `ACE`, `ACCESS_ALLOWED_ACE`, and `ACCESS_MASK`, then passes the serialized bytes to Windows Remote Authorization APIs.
- Examples such as `rbcd.py`, `dacledit.py`, `owneredit.py`, `badsuccessor.py`, and ntlmrelayx LDAP attacks are practical integration tests for constructing and modifying descriptors used by AD delegation and DACL workflows.
- Additional focused tests should cover descriptors with absent DACL/SACL/owner/group offsets, unknown ACE types, padded ACEs under both `RECALC_ACE_SIZE` settings, all ACE size alignment remainders, `ACCESS_MASK.removePriv()` idempotence, and SIDs with identifier authorities larger than one byte.
