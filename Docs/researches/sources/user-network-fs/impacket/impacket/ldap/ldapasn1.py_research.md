# sources/user-network-fs/impacket/impacket/ldap/ldapasn1.py

## Purpose

`ldapasn1.py` is Impacket's minimal RFC 4511 LDAP ASN.1 model with Active Directory extensions. It defines pyasn1 types for LDAP messages, request/response protocol operations, search filters, result codes, controls, and selected unsolicited notifications. The module is intentionally schema-oriented: callers build pyasn1 objects, BER-encode them for transport, decode LDAP responses into these classes, and use class identity such as `SearchResultEntry` or `SearchResultDone` to interpret results.

## Important APIs, types, and constants

- `CONTROL_PAGEDRESULTS` (`1.2.840.113556.1.4.319`) and `CONTROL_SDFLAGS` (`1.2.840.113556.1.4.801`) identify the implemented LDAP controls.
- `KNOWN_CONTROLS` maps control OIDs to specialized control classes. It is populated at module import with `SimplePagedResultsControl` and `SDFlagsControl`.
- `NOTIFICATION_DISCONNECT` and `KNOWN_NOTIFICATIONS` represent the LDAP notice-of-disconnection unsolicited notification.
- Primitive LDAP aliases include `MessageID`, `LDAPString`, `LDAPOID`, `LDAPDN`, `RelativeLDAPDN`, `AttributeDescription`, `AttributeValue`, `AssertionValue`, `MatchingRuleID`, and `URI`.
- Enumerations include `ResultCode`, `Scope`, `DerefAliases`, and `Operation`; these mirror LDAP result/status, search scope, alias handling, and modify operation values.
- Attribute containers include `AttributeValueAssertion`, `PartialAttribute`, `PartialAttributeList`, `Attribute`, `AttributeList`, `AttributeSelection`, and `Referral`.
- Operation schemas include `BindRequest`, `BindResponse`, `UnbindRequest`, `SearchRequest`, `SearchResultEntry`, `SearchResultReference`, `SearchResultDone`, `ModifyRequest`, `ModifyResponse`, `AddRequest`, `AddResponse`, `DelRequest`, `DelResponse`, `ModifyDNRequest`, `ModifyDNResponse`, `CompareRequest`, `CompareResponse`, `AbandonRequest`, `ExtendedRequest`, `ExtendedResponse`, and `IntermediateResponse`.
- `Filter` is a recursive `Choice` whose `componentType` is assigned after class creation so `and`, `or`, and `not` can contain nested `Filter` instances.
- `Control` is the base control schema. Its `setComponentByPosition()` hook upgrades the instance class to a known specialized control when component 0 (`controlType`) is set to a recognized OID.
- `SDFlagsControlValue` / `SDFlagsControl` BER-encode and decode the Active Directory security descriptor flags control.
- `SimplePagedResultsControlValue` / `SimplePagedResultsControl` BER-encode and decode RFC 2696 paged results parameters.
- `LDAPMessage` is the top-level message sequence: `messageID`, `protocolOp`, optional request/response controls, and two AD compatibility fields (`responseName`, `responseValue`) for non-conforming responses.

## Control flow and behavior

Most classes are declarative pyasn1 schemas; the significant behavior is in mixins and controls:

- `DefaultSequenceAndSetBaseMixin.getComponentByPosition()` walks base classes to call the pyasn1 implementation and instantiates a missing component with `setComponentByPosition(idx)` when pyasn1 returns `None`. This makes several request/filter objects easier to populate incrementally through chained indexing.
- `Control.setComponentByPosition()` watches for `controlType` assignment. If the OID exists in `KNOWN_CONTROLS`, it mutates `self.__class__` to the mapped subclass before delegating to `univ.Sequence.setComponentByPosition()`. This lets decoded or incrementally-built controls gain helper methods such as `getCookie()` after the OID is known.
- `Control.prettyPrint()` calls `decodeControlValue()` and, when a specialized control returns a decoded value, replaces the raw value rendering with the nested decoded sequence. Base `Control.decodeControlValue()` returns `None`.
- `SDFlagsControl.__init__()` sets OID, optional criticality, stores `flags`, and immediately BER-encodes `controlValue`. `getFlags()` decodes `controlValue` back to `_flags`; `setFlags()` updates `_flags` and re-encodes. The default `flags=0x00000007` requests owner, group, and DACL security information.
- `SimplePagedResultsControl.__init__()` sets OID, optional criticality, stores `_size` and `_cookie`, and encodes `controlValue`. `getSize()` and `getCookie()` decode before returning, so they reflect `controlValue` even after a server response is decoded into the same object shape.
- `LDAPMessage.protocolOp` is a `Choice` over all supported LDAP application tags. BER decoding chooses the matching class by tag; callers commonly test `isinstance(item, ldapasn1.SearchResultEntry)` after LDAP connection code unwraps messages.

## State and persistence behavior

The module has no external persistence, files, sockets, or database state. State is in pyasn1 object fields and module-level registries:

- `KNOWN_CONTROLS` is mutable global registration state. Adding entries changes how future `Control` objects specialize.
- Control helpers keep cached decoded/encoded values in instance attributes (`_size`, `_cookie`, `_flags`) plus ASN.1 fields (`controlValue`, `criticality`, `controlType`). The ASN.1 field is authoritative for getters because getters decode it before returning.
- `Control.setComponentByPosition()` mutates the Python class of an instance. That is unusual stateful behavior and can surprise code relying on exact class construction or subclass invariants.
- `LDAPMessage` and nested operation objects persist only as in-memory pyasn1 structures until callers encode or decode them with `pyasn1.codec.ber.encoder` / `decoder`.

## Dependencies and integration points

- Depends on `pyasn1.codec.ber.encoder`, `pyasn1.codec.ber.decoder`, and pyasn1 `univ`, `namedtype`, `namedval`, `tag`, and `constraint`.
- Imported and re-exported by `impacket/ldap/ldap.py`, which builds LDAP requests, decodes socket responses, handles bind/search/modify flows, and exposes `Control`, `SimplePagedResultsControl`, `ResultCode`, `Scope`, `DerefAliases`, `Operation`, `CONTROL_PAGEDRESULTS`, `KNOWN_CONTROLS`, `NOTIFICATION_DISCONNECT`, and `KNOWN_NOTIFICATIONS`.
- Used by examples such as `GetADComputers.py`, `GetLAPSPassword.py`, `GetUserSPNs.py`, `changepasswd.py`, and ntlmrelayx SOCKS LDAP handling to identify `SearchResultEntry`, construct `ModifyRequest`, use paged search controls, and interpret bind/search results.
- Integrates with `ldaptypes.py` through `CONTROL_SDFLAGS` / `SDFlagsControl`; callers use the control to request `nTSecurityDescriptor` portions and parse the returned binary value with `SR_SECURITY_DESCRIPTOR`.
- Supports Active Directory-specific authentication choices (`sicilyPackageDiscovery`, `sicilyNegotiate`, `sicilyResponse`) used by Impacket LDAP login code.

## Risks and edge cases

- `Control.setComponentByPosition()` class mutation is powerful but fragile. If a subclass `__init__` was not run, decoded controls rely on pyasn1-populated fields and helper methods must tolerate missing private attributes until decode occurs.
- `KNOWN_CONTROLS[value]` uses the assigned value directly. If pyasn1 supplies an `OctetString` object rather than a native string in some path, lookups may miss unless equality/hash behavior matches expectations.
- `DefaultSequenceAndSetBaseMixin.getComponentByPosition()` intentionally bypasses newer pyasn1 arguments (`default`, `instantiate`) in the delegated call. This compatibility shim may diverge from pyasn1 behavior after dependency upgrades.
- The recursive `Filter.not` branch is modeled as `SetOf(Filter())`, while the commented line suggests RFC-style single constructed filter was considered. This may accept or emit non-canonical encodings for NOT filters.
- Several fields are explicitly AD-specific or tolerant of AD non-conformance, including Sicily authentication alternatives and top-level `LDAPMessage.responseName` / `responseValue`. Strict LDAP peers or strict conformance tests may reject these shapes.
- `SimplePagedResultsControl` defaults `cookie=''`, a text string, while LDAP cookies are octet strings. pyasn1 often accepts this, but byte/string handling can be sensitive across Python and pyasn1 versions.
- `SDFlagsControl.setFlags()` writes `_flags` but `encodeControlValue()` reads `self.flags`, so after initialization `setFlags()` may not encode the newly assigned value. This is a concrete behavioral risk for callers trying to change SD flags dynamically.
- There is little validation beyond pyasn1 constraints. Semantic LDAP validation, server feature discovery, and unsupported controls are left to LDAP server responses or higher-level code.

## Test signals

- `tests/SMB_RPC/test_ldap.py` exercises LDAP bind flows (`sicilyPackageDiscovery`, NTLM Sicily, SASL NTLM, Kerberos variants), search responses, `SearchResultEntry` filtering, and security descriptor retrieval via LDAP.
- Examples exercise common schemas: paged search controls in `GetLAPSPassword.py` and `GetUserSPNs.py`, modify operations in `changepasswd.py`, and result-code stringification after LDAP modify operations.
- Useful focused tests would BER round-trip each protocol operation through `LDAPMessage`, verify recursive filters including `not`, assert decoded controls specialize to `SimplePagedResultsControl` / `SDFlagsControl`, and specifically cover `SDFlagsControl.setFlags()` changing encoded `controlValue`.
- Compatibility tests should pin byte-level encodings for simple bind, SASL bind, search with paged results, and search with SD flags because pyasn1 tag/constraint behavior is the primary integration contract.
