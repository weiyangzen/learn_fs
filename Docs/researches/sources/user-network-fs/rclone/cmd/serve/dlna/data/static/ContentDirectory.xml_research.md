# sources/user-network-fs/rclone/cmd/serve/dlna/data/static/ContentDirectory.xml

## Purpose

This SCPD document declares the UPnP ContentDirectory service contract for browse/search/media metadata discovery.

## Important APIs, Types, and Functions

The document lists actions including `GetSearchCapabilities`, `GetSortCapabilities`, `GetSystemUpdateID`, `Browse`, many optional transfer/mutation actions, and Samsung extension actions `X_GetFeatureList` and `X_SetBookmark`. It defines state variables for object IDs, browse flags, filters, counts, update IDs, feature lists, transfer status, URI arguments, and bookmark fields.

## Control Flow

DLNA clients read this XML to determine legal SOAP action names, argument names, argument directions, and expected output order. `cds.go` implements the read-oriented subset, especially `Browse`.

## State and Persistence Behavior

The file is static and embedded. It does not track actual content updates.

## Dependencies and Integration Points

It must stay consistent with `contentDirectoryService.Handle`, `soapArgs` ordering, and DIDL-Lite output. `dlna_test.go` explicitly protects Browse response argument order matching this XML.

## Risks and Test Signals

The XML advertises actions the implementation does not support, which may confuse aggressive clients. The highest-risk contract is Browse output order and XML entity compatibility; tests directly cover both.
