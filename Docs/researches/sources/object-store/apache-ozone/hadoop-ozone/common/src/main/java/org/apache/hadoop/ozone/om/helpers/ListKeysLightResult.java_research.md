# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListKeysLightResult.java

Purpose: Result container for lightweight key listing.

Important APIs/types/functions: Constructor stores `List<BasicOmKeyInfo>` and `isTruncated`. Getters expose both.

Control flow and state: No branching. The key list reference is mutable if the caller supplied a mutable list.

State and persistence behavior: Transport result only, not persisted.

Dependencies and integration points: Used by list-key APIs that return `BasicOmKeyInfo` instead of full `OmKeyInfo`.

Risks: No defensive copy or null validation.

Test signals: Listing tests should verify truncation and returned key order/contents for light-list paths.
