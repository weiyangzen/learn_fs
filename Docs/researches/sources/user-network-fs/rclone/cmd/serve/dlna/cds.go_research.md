# sources/user-network-fs/rclone/cmd/serve/dlna/cds.go

## Purpose

`cds.go` implements the DLNA ContentDirectory service over rclone VFS content, translating files and directories into DIDL-Lite UPnP AV objects.

## Important APIs, Types, and Functions

`contentDirectoryService` embeds the server and UPnP eventing. Key functions are `cdsObjectToUpnpavObject`, `readContainer`, `mediaWithResources`, `objectFromID`, `countChildren`, and `Handle`. `object` converts between cleaned absolute VFS paths, ObjectIDs, parent IDs, and local display paths.

## Control Flow

Browse requests are unmarshaled from SOAP XML, empty or `0` ObjectIDs resolve to root, and `BrowseDirectChildren` lists a VFS directory, folds in `Subs` children, sorts directories before files, associates subtitle resources, marshals UPnP AV objects, adjusts XML entities, and wraps the result in ordered SOAP args. `BrowseMetadata` stats one object and returns a single DIDL item or container. Unsupported actions become UPnP invalid action/value errors.

## State and Persistence Behavior

The service stores no durable state. `updateIDString` uses the process ID, so update IDs are process-lifetime signals rather than real content version counters.

## Dependencies and Integration Points

It depends on rclone VFS, MIME helpers, anacrolix UPnP/DLNA types, `upnpav` structs, HTTP request host names for resource URLs, and service descriptions in `ContentDirectory.xml`.

## Risks and Test Signals

Risks include expensive full-directory reads, ObjectID/path escaping corner cases, subtitle matching across mixed directories, MIME misclassification, Samsung/XML compatibility regressions, and a TODO that BrowseMetadata omits external subtitles. `cds_test.go` exercises subtitle association, title trimming, SOAP escaping, and resource inclusion; `dlna_test.go` exercises live SOAP browse calls.
