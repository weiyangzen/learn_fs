# sources/user-network-fs/rclone/backend/jottacloud/api/types_test.go

## Purpose
Provides a focused regression test for Jottacloud XML time parsing when a mountpoint response contains an empty modification time.

## Important APIs, Types, and Functions
`TestMountpointEmptyModificationTime` builds a sample `<mountPoint>` XML document, unmarshals it into `JottaFolder`, and asserts `ModifiedAt` is zero.

## Control Flow
The test feeds XML with `<modified></modified>` into `xml.Unmarshal`. This exercises `JottaTime.UnmarshalXML` through `unmarshalXMLTime`, which treats an empty string as zero time and nil error.

## State and Persistence
No persistent state. The XML fixture is embedded in the test.

## Dependencies and Integration Points
Uses standard `encoding/xml`, `testing`, and `time`. It validates the behavior required by real Jottacloud mountpoint/folder responses that can include empty modification fields.

## Risks and Edge Cases
The test unmarshals into `JottaFolder` despite the fixture being a mountpoint; this works because the fields under test overlap, but it does not validate `JottaMountPoint` directly. It does not test non-empty classic time values, invalid time strings, or `Rfc3339Time`.

## Test Signals
The key signal is that empty XML times must stay non-fatal and become zero values. This protects listing code from failing on mountpoints with blank modification timestamps.
