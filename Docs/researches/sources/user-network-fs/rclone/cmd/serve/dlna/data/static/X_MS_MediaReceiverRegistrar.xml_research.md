# sources/user-network-fs/rclone/cmd/serve/dlna/data/static/X_MS_MediaReceiverRegistrar.xml

## Purpose

This SCPD document declares Microsoft's MediaReceiverRegistrar compatibility service.

## Important APIs, Types, and Functions

It declares `IsAuthorized`, `RegisterDevice`, and `IsValidated`, with argument/state variables for device IDs, result integers, registration request/response blobs, and authorization/validation update IDs.

## Control Flow

Clients discover the service from the root descriptor and call SOAP actions at the shared control URL. `mrrs.go` fakes positive authorization/validation and returns the server UUID for registration.

## State and Persistence Behavior

The XML is static; no authorization registry is persisted.

## Dependencies and Integration Points

It is embedded through `data.Assets` and must match `mediaReceiverRegistrarService.Handle` response argument names.

## Risks and Test Signals

The implementation is deliberately permissive and not a security control. `TestMediaReceiverRegistrarService` verifies `RegisterDevice` is reachable and returns `RegistrationRespMsg`.
