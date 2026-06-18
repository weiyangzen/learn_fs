# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ListOpenFilesResult.java

Purpose: Result container for listing open files/open keys, including total count, continuation token, `hasMore`, and `OpenKeySession` entries.

Important APIs/types/functions: One constructor accepts ready `OpenKeySession` objects; another accepts parallel client ID and protobuf `KeyInfo` lists and converts them through `getOpenKeySessionListFromPB`. JSON properties name `totalOpenKeyCount`, `hasMore`, and `contToken`.

Control flow and state: Conversion validates equal list sizes, parses each `KeyInfo` into `OmKeyInfo`, and sets session version from the latest key-location version.

State and persistence behavior: Transport/admin result only. The protobuf constructor reconstructs key metadata from serialized forms but does not write DB state.

Dependencies and integration points: Used by open-file listing/admin APIs. Depends on Guava preconditions, Jackson annotations, `OpenKeySession`, and `OmKeyInfo`.

Risks: If key info has no latest version locations, session version lookup can fail. No defensive copy of session list.

Test signals: Mismatched list size rejection, protobuf conversion with multiple open keys, JSON property names, continuation token/hasMore behavior, and empty result handling.
