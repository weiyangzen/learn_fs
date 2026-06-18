<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OpenKeySession.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OpenKeySession.java

## Purpose

`OpenKeySession` represents an active client session for an opened key. It lets OM and clients associate a client ID with the `OmKeyInfo` being written and the key version opened by that session.

## Important APIs, Types, And Functions

The constructor stores `id`, `keyInfo`, and `openVersion`. Getters expose the session ID, key info, and open version. The ID is annotated with Jackson `@JsonProperty("clientId")`.

## Control Flow, State, And Persistence

The object is returned by open/create-file APIs and later referenced by commit, hsync, recover, or allocate-block calls using the client ID. It is not the authoritative persisted open-key row, but it mirrors state stored in OM open key tables.

## Dependencies And Integration Points

It depends on `OmKeyInfo` and Jackson. It integrates with `OzoneManagerProtocol.openKey`, `createFile`, `allocateBlock`, `commitKey`, `hsyncKey`, and lease recovery.

## Risks And Test Signals

`openVersion` is mutable but has no setter, and `keyInfo` may itself contain mutable block metadata. Tests should cover open-create-commit round trips, JSON field compatibility, multipart/open-version behavior, and recovery of sessions with pending blocks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OpenKeySession.java -->
