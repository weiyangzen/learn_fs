# Research: sources/user-network-fs/impacket/impacket/mapi_constants.py

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009630`: lines 1-2895, `Docs/researches/chunks/subset-b-009630_research.md`
- `subset-b-009631`: lines 2896-3582, `Docs/researches/chunks/subset-b-009631_research.md`

## Chunk Research

### subset-b-009630: lines 1-2895

# `sources/user-network-fs/impacket/impacket/mapi_constants.py` Lines 1-2895

## Purpose

This chunk defines Impacket's MAPI/Exchange constant catalog for NSPI, OXABREF, and the `examples/exchanger.py` tooling. It is a data-only module: importing it creates lookup dictionaries and integer constants used to decode MAPI HRESULTs, address book display/object metadata, address book container flags, and a large property-id metadata table.

The top of the file cites MAPI error and property references, then exposes four main lookup surfaces:

- `ERROR_MESSAGES`: MAPI, SYNC, and LDAP-style error codes mapped to symbolic names.
- `PR_DISPLAY_TYPE_VALUES`: `PR_DISPLAY_TYPE` numeric values for address-book, hierarchy, and folder rows.
- `PR_OBJECT_TYPE_VALUES`: MAPI object type IDs such as stores, folders, messages, attachments, sessions, and address book containers.
- `PR_CONTAINER_FLAGS_VALUES`: NSPI address book container bit flags.
- `MAPI_PROPERTIES`: property ID metadata mapping MAPI property IDs to type, Active Directory schema names, documented MS-OXPROPS names, alternate `PR_*` names, and Exchange internal names.

## Important APIs, Types, And Constants

There are no functions or classes in this line range. The public API is the module namespace itself.

`ERROR_MESSAGES` maps integer HRESULT-like status values to a single symbolic string, for example `MAPI_E_NOT_FOUND`, `MAPI_E_LOGON_FAILED`, `MAPI_E_NO_ACCESS`, `SYNC_E_CONFLICT`, and LDAP-related names such as `LDAP_SERVER_DOWN`. Lines 113-201 also publish the same numeric values as module-level constants, so callers can either compare against constants or lookup status names.

`PR_DISPLAY_TYPE_VALUES` is paired with constants such as `DT_MAILUSER`, `DT_DISTLIST`, `DT_GLOBAL`, `DT_FOLDER`, and `DT_FOLDER_SPECIAL`. It is intended for decoding `PR_DISPLAY_TYPE` values in address book contents, hierarchy, and folder hierarchy tables.

`PR_OBJECT_TYPE_VALUES` is paired with constants such as `MAPI_STORE`, `MAPI_ADDRBOOK`, `MAPI_FOLDER`, `MAPI_MESSAGE`, `MAPI_ATTACH`, and `MAPI_DISTLIST`. It gives string names for object type numeric values found in MAPI objects.

`PR_CONTAINER_FLAGS_VALUES` names bit values such as `AB_RECIPIENTS`, `AB_SUBCONTAINERS`, `AB_MODIFIABLE`, `AB_FIND_ON_OPEN`, and `AB_CONF_ROOMS`. `examples/exchanger.py` passes this dictionary into its `parse_bitmask()` helper to render NSPI hierarchy flags.

`MAPI_PROPERTIES` is the core table. Each key is a property ID, not a full property tag. Each value is an eight-field tuple:

`(PropertyType, ldapDisplayName, activeDirectoryCN, partialAttributeSetState, canonicalName, firstAlternateName, exchangeInternalName)`

The in-file comments define `partialAttributeSetState` as `1` for true, `2` for false, `3` for missing, and `4` for non-Active-Directory properties. Property types use MAPI property type IDs, including common values like `0x001f` Unicode string, `0x101f` multivalue Unicode string, `0x0003` integer, `0x000b` boolean, `0x0040` FILETIME, `0x0102` binary, `0x1102` multivalue binary, `0x000d` object/embedded table, and less common forms such as `0x0014` 64-bit integer and `0x0048` GUID.

## Table Coverage In This Chunk

The first part of `MAPI_PROPERTIES` covers address-book and Active Directory-backed Exchange attributes. Examples include identity and display attributes (`displayNamePrintable`, `mailNickname`, `givenName`, `sn`, `company`, `title`, `department`), contact details (`telephoneNumber`, `homePhone`, `mobile`, `pager`, address fields), certificates and object identity (`userCert`, `userSMIMECertificate`, `objectSid`, `objectGUID`, `thumbnailPhoto`), mailbox and routing data (`homeMDB`, `homeMTA`, `proxyAddresses`, `targetAddress`, delivery restrictions), moderation and hierarchical address book properties, resource room metadata, and extension attributes.

The middle of the table switches to non-AD named and tagged MAPI properties with state `4`. It includes Outlook/Exchange property families for appointments, recurrence, reminders, tasks, contacts, notes, RSS posts, sharing, conversation actions, body formats, recipients, delivery reports, attachments, folders, rules, search folders, free/busy, junk mail, retention, views, sync/change tracking, and store/profile configuration.

The later lines in this chunk add many Exchange internal and mailbox-store fields where canonical and alternate names are absent but internal names are present. These cover profile and transport state, store well-known folder entry IDs, search indexing fields, OOF and assistant control data, public folder and quota fields, logon and resource counters, conversation aggregate fields, mailbox user information properties, BigFunnel/MCDB indexing metrics, compliance/retention assistants, group mailbox state, and resource usage aggregation.

## Control Flow

This file has no runtime branching, loops, parsing, IO, or protocol calls in the requested range. Control flow is limited to Python import-time evaluation of literal assignments. Consumers perform lookup operations after import.

The effective lookup flow in downstream code is:

1. Import `mapi_constants`.
2. For an RPC/MAPI error code, test membership in `ERROR_MESSAGES` and render the symbolic string.
3. For address-book flag bitmasks, use `PR_CONTAINER_FLAGS_VALUES` to translate set bits.
4. For NSPI row properties, derive `PropertyId = aulPropTag >> 16` and `PropertyType = aulPropTag & 0xffff`; then use `MAPI_PROPERTIES[PropertyId]` to choose a display name.

`examples/exchanger.py` prefers `MAPI_PROPERTIES[PropertyId][1]` (`ldapDisplayName`) for row output, then falls back to the canonical MS-OXPROPS name and finally the Exchange internal name. This means tuple field ordering is a contract, not incidental formatting.

## State And Persistence Behavior

The module owns only immutable-looking module globals, but the dictionaries are ordinary mutable Python dictionaries. No code in this chunk persists data, opens files, writes network state, caches computed values, or protects the tables against mutation by importers.

Because table construction happens at import time, every importing process pays the memory cost of a large `MAPI_PROPERTIES` dictionary. There is no lazy loading and no validation pass over duplicate property IDs or tuple shape.

## Dependencies

This chunk has no imports. It depends only on Python literal syntax and the external correctness of the referenced Microsoft/Exchange property data. Downstream modules depend on it:

- `impacket/dcerpc/v5/nspi.py` imports `mapi_constants` and uses `ERROR_MESSAGES` in `DCERPCSessionError.__str__`.
- `impacket/dcerpc/v5/oxabref.py` does the same for OXABREF errors.
- `examples/exchanger.py` imports `PR_CONTAINER_FLAGS_VALUES` and `MAPI_PROPERTIES` for address-book hierarchy and property row rendering.

## Integration Points

The NSPI and OXABREF integrations expect `ERROR_MESSAGES` values to be strings. This differs from Impacket's generic `hresult_errors.ERROR_MESSAGES`, where values are two-item tuples. Code in `nspi.py` and `oxabref.py` correctly treats MAPI constants as direct strings and hresult entries as tuples.

The address-book tooling integrates at the property-tag level by extracting the high 16-bit property ID before indexing `MAPI_PROPERTIES`. As a result, type variants of the same property ID share the same metadata row. This fits the table's design but can lose information if a property ID is returned with a type different from the table's preferred or Unicode type.

The display/object/flag maps are intended for user-readable decoding and diagnostics rather than protocol serialization. The numeric constants are still useful for comparisons in new protocol helpers.

## Risks And Edge Cases

Duplicate property IDs are a structural risk. Python silently keeps the last entry for a duplicated key, so a later row can override earlier metadata without warning. This matters because `MAPI_PROPERTIES` combines AD attributes, named properties, tagged properties, and internal Exchange names in a single dictionary keyed only by property ID.

The `ERROR_MESSAGES` value shape is inconsistent with other Impacket error tables. New callers might assume tuple values and incorrectly index strings, or might accidentally pass these values into formatting code written for `hresult_errors`.

The property table is authoritative-looking but not self-validating. Typos in symbolic names, internal names, property types, or partial attribute state values will only surface as misleading decoded output. The module also includes legacy and internal Exchange properties that may not be stable across server versions.

Because `MAPI_PROPERTIES` is keyed by property ID only, named properties that share an ID in different property sets cannot be disambiguated by GUID/property-set context. Callers needing exact named-property identity must combine this table with named-property mapping data from protocol responses.

The table defaults to Unicode variants where possible. That is useful for display, but callers constructing exact property tags must not blindly combine a returned property ID with the table's stored type when the server supplied another type or an error type such as `0x000a`.

## Test Signals

Useful low-level checks for this chunk are import and shape checks:

- `python -m py_compile impacket/mapi_constants.py` should succeed.
- Importing `impacket.mapi_constants` should expose `ERROR_MESSAGES`, `PR_DISPLAY_TYPE_VALUES`, `PR_OBJECT_TYPE_VALUES`, `PR_CONTAINER_FLAGS_VALUES`, and `MAPI_PROPERTIES`.
- Every `MAPI_PROPERTIES` value should be a tuple of length 7, matching the comment's fields 2-8.
- Known lookups should remain stable: `MAPI_E_NOT_FOUND` should equal `0x8004010f`, `ERROR_MESSAGES[0x8004010f]` should name `MAPI_E_NOT_FOUND`, `PR_CONTAINER_FLAGS_VALUES[0x00000002]` should name `AB_SUBCONTAINERS`, and `MAPI_PROPERTIES[0x3001]` should identify display name metadata.

Integration tests should exercise `examples/exchanger.py` row rendering with known property tags for an AD-backed property, a documented MAPI-only property, and an internal-name-only property. Error formatting tests for `nspi.DCERPCSessionError` and `oxabref.DCERPCSessionError` should include one MAPI error and one generic HRESULT fallback to catch the string-versus-tuple distinction.

### subset-b-009631: lines 2896-3582

# sources/user-network-fs/impacket/impacket/mapi_constants.py lines 2896-3582

## Scope

This chunk is the final slice of `MAPI_PROPERTIES` in `impacket/mapi_constants.py`. It starts at property id `0x35eb` (`UMVoicemailFolderEntryId`) and runs through the dictionary close at EOF, ending with `0x8d0d` (`ExternalDirectoryObjectId`). The range contains 686 MAPI property-id entries.

The source is declarative constant data, not executable protocol logic. Each entry maps a 16-bit MAPI property id to a seven-element tuple documented near the start of `MAPI_PROPERTIES`: property type, optional Active Directory LDAP display name, optional Active Directory CN, partial-attribute-set status, optional MS-OXPROPS canonical name, optional PR-style alternate name, and internal Exchange property name. In this chunk all entries have AD metadata and public canonical names set to `None`, the partial-attribute-set classification set to `4`, and the internal Exchange name populated.

## Purpose

`MAPI_PROPERTIES` is Impacket's local lookup table for translating property ids observed in Exchange/MAPI responses into readable names and expected MAPI property types. This chunk extends the table with non-Active-Directory, largely Exchange-internal properties covering folder identifiers, search and indexing state, BigFunnel and assistant control data, FastTransfer/incremental sync markers, replication identifiers, mailbox quota and profile state, event and inference telemetry, conversation/person/signal metadata, user photo/cache fields, and cloud or compliance-related flags.

Because this is the tail of the table, it also owns the syntactic close of `MAPI_PROPERTIES`; malformed edits here can break import of the whole `impacket.mapi_constants` module.

## Data Shape And Important APIs

There are no functions or classes in this line range. The exported API affected by the chunk is the module-level dictionary:

- `MAPI_PROPERTIES[property_id][0]`: MAPI property type. Common values in this range include `0x0102` binary, `0x0003` 32-bit integer, `0x001f` Unicode string, `0x000b` Boolean, `0x0040` FILETIME, `0x0014` 64-bit integer, `0x0048` GUID, plus multivalue forms such as `0x101f`, `0x1003`, `0x1102`, and `0x1014`.
- `MAPI_PROPERTIES[property_id][1]` and `[2]`: Active Directory names. In this chunk they are consistently `None`.
- `MAPI_PROPERTIES[property_id][3]`: classification value. Every entry in this chunk uses `4`, meaning "not an Active Directory property" per the table comment.
- `MAPI_PROPERTIES[property_id][4]` and `[5]`: canonical and PR alternate names. These are also consistently `None` in this chunk.
- `MAPI_PROPERTIES[property_id][6]`: internal Exchange name. This is the meaningful display label for every property in the chunk.

Type distribution in the assigned range is a useful maintenance signal: 225 binary properties, 168 integer32 properties, 130 Unicode string properties, 61 Boolean properties, 32 FILETIME properties, 25 integer64 properties, 12 GUID properties, and a small set of multivalue string/integer/binary/GUID variants.

## Property Families Covered

The `0x35xx` and `0x36xx` entries are mostly folder, mailbox, and search/indexing identifiers: Recoverable Items folders (`DeletionsFolderEntryId`, `PurgesFolderEntryId`, `DiscoveryHoldsFolderEntryId`, `VersionsFolderEntryId`), archive/system/public folder entry ids, packed named properties, content indexing flags, search folder diagnostics, BigFunnel point-of-interest fields, folder views, aging policy, public folder split/processor state, and low-latency container quota fields.

The `0x3dxx` and `0x3exx` groups add security descriptor and ACL fields, BigFunnel posting-list maintenance state, mailbox move and tenant hints, internal conversation/change keys, virtual read/unread state, identity/resource/status fields, and remote-progress fields.

The `0x3fxx` and `0x40xx` groups include control layout metadata, attachment and replica identifiers, ACL checksums, rule/move targets, quota type, FastTransfer stream markers (`StartMessage`, `EndAttachment`, `IncrSyncChange`, `FastTransferDelProp`, `IdsetGiven`), sender/recipient flag fields, creator/modifier/report address fields, original-address variants, and incremental sync progress/control properties.

The `0x5dxx`, `0x60xx`, `0x65xx`, `0x66xx`, and `0x67xx` groups cover SMTP address variants, SIP URI, RSS lock state, scheduling/rule message blobs, profile settings, deleted item counts, ICS/change keys, internet content, mailbox/folder quota counters, replication timing/status, mailbox ownership, delivery policy, reserved counter ranges, public folder search/categorization sets, change-number sets, CAI address identity blobs, and ICS view/filter metadata.

The `0x68xx` and `0x69xx` groups are dominated by event, inference, activity, delegate, immutable id, person, conversation, and signal telemetry properties. They include event folder/message ids, inference session/window ids, activity container ids, delegate entry ids/flags, mailbox-wide person fields, conversation preview/member/category/thread/mention state, and client signal fields such as app id, tenant id, device id, IP, user agent, location, locale, and timestamp.

The `0x70xx`, `0x7cxx`, `0x7dxx`, `0x7fxx`, and final `0x8d0d` entries add assistant control blobs, People Relevance counters, mailbox feature storage, favorites and sync state, photo cache ids, immutable id replacement/cloud-cache status, dynamic time-based assistant control data, tenant size estimate, ATP/DLP markers, and `ExternalDirectoryObjectId`.

## Control Flow

There is no runtime branching in this chunk. The only control-flow effect is Python import-time evaluation of the dictionary literal. After import, callers perform ordinary dictionary lookup by property id.

The main consumer found in this source tree is `examples/exchanger.py`. Its `print_row` method derives `PropertyId = aulPropTag >> 16`, checks membership in `MAPI_PROPERTIES`, then chooses a display name from tuple index `[1]`, falling back to `[5]`, then `[6]`. For this chunk, the fallback to `[6]` is the path that produces useful names because all LDAP and alternate-name fields are `None`.

## State And Persistence Behavior

This chunk does not persist data and has no mutable internal state beyond the module-level dictionary object. The dictionary is effectively static reference data for a running process.

The represented properties themselves often name persistent Exchange mailbox, folder, sync, replication, assistant, telemetry, or compliance state, but `mapi_constants.py` only labels those wire/storage properties. It does not parse, validate, serialize, or store their values.

## Dependencies And Integration Points

Direct dependencies are minimal: this module uses only Python literals. It is imported by:

- `examples/exchanger.py`, which imports `MAPI_PROPERTIES` and `PR_CONTAINER_FLAGS_VALUES` to render Exchange/NPSI table rows and container flags in human-readable form.
- `impacket.dcerpc.v5.nspi` and `impacket.dcerpc.v5.oxabref`, which import `mapi_constants` for MAPI error lookup from earlier parts of the same module.

The practical integration contract for this chunk is tuple compatibility with the table comment and with `exchanger.py`'s hard-coded tuple indices. Property ids must remain integer keys, property types must stay numeric, and internal Exchange names must remain strings for entries that lack public names.

## Risks And Maintenance Notes

The highest-risk issue is silent tuple-index drift. There is no named structure or accessor, so adding/removing/reordering tuple fields would break callers that use numeric indexes. This is especially visible in `exchanger.py`, where chunk entries depend on index `[6]` as the display-name fallback.

The table mixes official-looking and internal Exchange property names without local validation against MS-OXPROPS or server behavior. Incorrect property ids or types would not fail import, but they would mislabel Exchange output or confuse downstream tooling that assumes the type code is authoritative.

Because this chunk closes the `MAPI_PROPERTIES` literal and the file, trailing comma, brace, or indentation mistakes can make the whole module fail to import. Duplicate property ids in the dictionary would also be accepted by Python with last-write-wins semantics, so uniqueness should be checked mechanically when editing.

Several names reflect mailbox telemetry or client signal data (`SignalClientIp`, `SignalUserAgent`, location fields). This module only exposes labels, but tools that print values for these property ids can surface sensitive operational metadata.

## Test Signals

Useful validation signals for this chunk include:

- `python -m py_compile impacket/mapi_constants.py` or importing `impacket.mapi_constants` successfully.
- Assert that `MAPI_PROPERTIES[0x35eb] == (0x0102, None, None, 4, None, None, "UMVoicemailFolderEntryId")`.
- Assert that `MAPI_PROPERTIES[0x8d0d] == (0x001f, None, None, 4, None, None, "ExternalDirectoryObjectId")`.
- Count 686 property entries in lines 2896-3582, with first key `0x35eb` and last key `0x8d0d`.
- Spot-check consumer behavior in `examples/exchanger.py` by rendering a property tag whose high word is a chunk id, such as `0x35eb0102`, and verifying the display name falls back to the internal Exchange name.
- Run a duplicate-key scan over `MAPI_PROPERTIES` source literals if the table is regenerated or manually edited, because Python import alone will not expose overwritten keys.
