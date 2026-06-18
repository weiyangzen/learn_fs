# sources/user-network-fs/rclone/cmd/serve/dlna/mrrs.go

## Purpose

`mrrs.go` implements a minimal Microsoft MediaReceiverRegistrar service for DLNA client compatibility.

## Important APIs, Types, and Functions

`mediaReceiverRegistrarService.Handle` supports `IsAuthorized`, `IsValidated`, and `RegisterDevice`.

## Control Flow

Authorization and validation actions return `Result=1`. `RegisterDevice` returns `RegistrationRespMsg` containing the server root device UUID. Any other action returns `upnp.InvalidActionError`.

## State and Persistence Behavior

No device registry, authorization table, or validation state is stored. Responses are stateless and permissive.

## Dependencies and Integration Points

The service is registered in `newServer`, described by `X_MS_MediaReceiverRegistrar.xml`, and tested through the shared SOAP control endpoint.

## Risks and Test Signals

This should not be interpreted as authentication; it is compatibility scaffolding. Tests verify `RegisterDevice` response presence, but not the two boolean actions or invalid-action behavior.
