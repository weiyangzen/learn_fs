<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/empty.go -->
# sources/sync-backup/kopia/notification/notifydata/empty.go

- Purpose: Defines the empty notification event payload.
- Important APIs/types/functions: `EmptyEventData`, `EventArgsType`.
- Control flow: `EventArgsType` returns the gRPC enum for empty arguments.
- State and persistence: Stateless JSON object payload.
- Dependencies and integration points: Used by test notifications and remote notification transport.
- Risks and edge cases: Enum value must stay synchronized with `UnmarshalEventArgs`.
- Test signals: `empty_test.go` round-trips the payload.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/empty.go -->
