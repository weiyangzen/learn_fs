# sources/user-network-fs/rclone/cmd/serve/dlna/cms.go

## Purpose

`cms.go` implements the DLNA ConnectionManager service.

## Important APIs, Types, and Functions

`defaultProtocolInfo` is the advertised source protocol string for many common video, audio, and image MIME types. `connectionManagerService.Handle` supports only `GetProtocolInfo`.

## Control Flow

When the SOAP action is `GetProtocolInfo`, the handler returns ordered args `Source` and `Sink`; all other actions return `upnp.InvalidActionError`.

## State and Persistence Behavior

The service has no mutable state beyond embedded eventing support inherited from anacrolix.

## Dependencies and Integration Points

It is registered from `dlna.go` under the `ConnectionManager` service key and must remain consistent with `ConnectionManager.xml` action and argument definitions.

## Risks and Test Signals

The advertised protocol string is static and may overstate support because rclone does not transcode. There are indirect tests through root descriptor discovery, but no dedicated action-level tests for unsupported ConnectionManager actions.
