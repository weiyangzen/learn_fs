<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/typed_event_args_test.go -->
# sources/sync-backup/kopia/notification/notifydata/typed_event_args_test.go

- Purpose: Tests notification event argument dispatch and shared JSON round-trip behavior.
- Important APIs/types/functions: `TestUnmarshalEventArgs`, `testRoundTrip`.
- Control flow: Iterates gRPC enum names except unknown, unmarshals `{}` for each supported type, and round-trips payloads through JSON plus `EventArgsType`.
- State and persistence: In-memory JSON only.
- Dependencies and integration points: Integrates `grpcapi` enum map and all typed event payloads.
- Risks and edge cases: Empty JSON validates type dispatch but not all populated field combinations.
- Test signals: Direct coverage for `typed_event_args.go` and shared support for other notifydata tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/typed_event_args_test.go -->
