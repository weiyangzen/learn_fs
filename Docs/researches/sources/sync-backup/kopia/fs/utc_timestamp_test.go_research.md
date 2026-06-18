## sources/sync-backup/kopia/fs/utc_timestamp_test.go

Purpose: unit tests for `fs.UTCTimestamp`.

Important APIs/types/functions: `TestUTCTimestamp`.

Control flow, state, and persistence: constructs precise UTC and offset timestamps, marshals/unmarshals through JSON structs, and asserts the stored nanosecond value and UTC formatted output. No external state.

Dependencies and integration points: tests Go `encoding/json` integration and public `fs` timestamp helpers.

Risks and test signals: confirms offset input is normalized to UTC, nanosecond values survive JSON, comparison helpers behave consistently, and invalid input returns an error containing the wrapper message.
