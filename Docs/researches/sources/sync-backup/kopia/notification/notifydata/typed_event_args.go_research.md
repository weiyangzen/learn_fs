<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/typed_event_args.go -->
# sources/sync-backup/kopia/notification/notifydata/typed_event_args.go

- Purpose: Defines the notification event argument interface and JSON unmarshal dispatch by gRPC enum.
- Important APIs/types/functions: `TypedEventArgs`, `UnmarshalEventArgs`.
- Control flow: Switches on `NotificationEventArgType`, allocates the matching payload struct, unmarshals JSON into it, and returns unsupported-type errors otherwise.
- State and persistence: In-memory JSON decoding for remote notification transport.
- Dependencies and integration points: Must stay aligned with `EmptyEventData`, `MultiSnapshotStatus`, `ErrorInfo`, and gRPC enum definitions.
- Risks and edge cases: Unknown enum values fail; adding a new payload type requires updating this switch and tests.
- Test signals: `typed_event_args_test.go` iterates known enum values and round-trips payloads.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/typed_event_args.go -->
