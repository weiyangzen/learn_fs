# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListKeysResult.java

Purpose: Result container for full key listing.

Important APIs/types/functions: Constructor stores `List<OmKeyInfo>` and `isTruncated`. Getters expose both.

Control flow and state: No branching. The key list is not defensively copied.

State and persistence behavior: Transport result only; contained `OmKeyInfo` values may be persisted OM key metadata.

Dependencies and integration points: Used by OM list-key APIs that need full key metadata and possibly block locations.

Risks: Mutable list exposure and no null validation.

Test signals: Listing tests should verify truncation, pagination marker behavior in caller code, and correct `OmKeyInfo` conversion.
