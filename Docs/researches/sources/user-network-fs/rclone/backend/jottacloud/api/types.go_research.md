# sources/user-network-fs/rclone/backend/jottacloud/api/types.go

## Purpose
Defines shared Jottacloud API data models and XML/JSON time helpers for both classic XML endpoints and newer JSON endpoints.

## Important APIs, Types, and Functions
Time helpers include `jottaTimeFormat`, `unmarshalXMLTime`, `JottaTime`, and `Rfc3339Time`, with XML marshal/unmarshal and RFC3339 JSON marshal for the latter. Auth/config models include `LoginToken`, `WellKnown`, and `TokenJSON`. Newer JSON upload/account models include `AllocateFileRequest`, `AllocateFileResponse`, `UploadResponse`, `DeviceRegistrationResponse`, `CustomerInfo`, and `TrashResponse`.

Classic XML models include `Flag`, `DriveInfo`, `JottaDevice`, `JottaMountPoint`, `JottaFolder`, `JottaFile`, and `Error`. `Flag` marks an XML attribute as present during unmarshalling, mainly for deleted flags. `Error.Error` formats Jottacloud error responses.

## Control Flow
XML time unmarshalling decodes element text, returns zero time for empty strings, and parses either Jottacloud's classic `2006-01-02-T15:04:05Z0700` format or standard RFC3339 depending on wrapper type. XML structs map nested account/device/mountpoint/folder/file responses into Go fields. JSON structs are plain DTOs for OAuth/device/upload/account endpoints.

## State and Persistence
This file stores no runtime state. It defines serialization contracts used by higher-level Jottacloud API code. Zero times represent empty XML time elements, which is important for mountpoints and folders that may omit modification times.

## Dependencies and Integration Points
Uses standard `encoding/xml`, `errors`, `fmt`, and `time`. Backend API callers depend on these models for unmarshalling remote responses and marshaling request times.

## Risks and Edge Cases
`TokenJSON.ExpiresIn` is `int32` despite a comment that some providers return strings, so string values would need custom handling elsewhere or fail unmarshalling. `Flag.MarshalXMLAttr` always returns an error and is explicitly not for use. `JottaTime.String` formats zero time as year 1 rather than an empty string, which is acceptable only if callers avoid marshaling absent times. Metadata structs model only selected response fields.

## Test Signals
`types_test.go` covers one important XML edge case: empty `<modified></modified>` unmarshals to zero time without error. There are no tests for RFC3339 time, JSON token oddities, `Flag`, or error formatting.
