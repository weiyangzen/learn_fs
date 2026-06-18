# sources/sync-backup/kopia/repo/object/objectid.go

Purpose: defines the compact object identifier format used by Kopia object storage. Object IDs wrap content IDs and add optional indirection (`I`) and compression (`Z`) prefixes.

Important APIs/types/functions: `ID` stores `content.ID`, `indirection`, and `compression`. Public methods/functions include `String`, `Append`, `MarshalJSON`, `UnmarshalJSON`, `IndexObjectID`, `ContentID`, `IDsFromStrings`, `IDsToStrings`, `DirectObjectID`, and `ParseID`. Package helpers include `compressed` and `indirectObjectID`; `EmptyID` is the zero object ID.

Control flow: string formatting emits `I` repeated for indirection, then `Z` for direct compressed content, then the content ID. Parsing consumes leading `I`s, optional `Z`, optional legacy `D`, rejects simultaneous indirection and compression, and delegates the remaining bytes to `content/index.ParseID`.

State and persistence behavior: IDs are value types and persist as JSON strings. Indirect IDs do not point straight to content; `IndexObjectID` decrements indirection to obtain the object ID that stores the next-level index. `ContentID` returns false for indirect IDs and returns the compressed flag for direct IDs.

Dependencies/integration: integrates with the content index ID parser and all object reader/writer paths. Snapshot manifests and repository APIs persist object IDs via JSON marshaling.

Risks: the legacy `D` prefix remains accepted, so parsing rules must stay compatible with old repositories. Compression and indirection are mutually exclusive at the same level; allowing both would make reader dispatch ambiguous. `Append` and `String` must remain byte-for-byte compatible because tests and manifests rely on stable IDs.

Test signals: `objectid_test.go` covers valid/invalid parse forms, string/list conversion, and string rendering for direct, indirect, and compressed IDs.
