# sources/user-network-fs/rclone/cmd/serve/dlna/upnpav/upnpav.go

## Purpose

This file defines the XML model used to marshal rclone VFS nodes into UPnP AV DIDL-Lite objects.

## Important APIs, Types, and Functions

Types are `Resource`, `Container`, `Item`, `Object`, and `Timestamp`. `NoSuchObjectErrorCode` maps ContentDirectory missing-object errors to UPnP code 701. `Timestamp.MarshalXML` formats non-zero dates as `YYYY-MM-DD`.

## Control Flow

`encoding/xml` uses struct tags to emit `res`, `container`, `item`, `dc:title`, `upnp:class`, resources, attributes, and inner XML. Zero timestamps omit date elements.

## State and Persistence Behavior

These are pure value types with no persistence.

## Dependencies and Integration Points

`cds.go` constructs these values before wrapping XML in DIDL-Lite. The XML namespace prefixes are supplied by `didlLite`.

## Risks and Test Signals

The struct tags are a wire contract with DLNA clients. Risks include missing optional metadata, wrong class strings, zero date omission differences, and XML namespace assumptions. Integration tests inspect resulting DIDL fragments but do not validate against a DIDL schema.
