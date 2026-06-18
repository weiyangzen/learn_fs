# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/CancelSnapshotDiffResponse.java

Purpose: Simple response DTO for cancel-snapshot-diff calls.

Important APIs and types: Stores a message string exposed by `getMessage` and `toString`. Nested `CancelMessage` enum defines canonical user-facing messages for cancel outcomes.

Control flow: Constructor assigns the message; enum constants each carry a message retrievable by `getMessage`.

State and persistence behavior: In-memory response object. Message values may cross client/server API boundaries but this class does not persist state.

Dependencies and integration points: Returned by `OzoneManagerProtocolClientSideTranslatorPB.cancelSnapshotDiff` after reading the server response reason.

Risks: Message strings are user-facing and may be asserted by CLI tests. Some enum messages encode state transitions and should remain synchronized with server cancel logic.

Test signals: Verify response/toString returns server reason and enum messages match expected CLI output.
