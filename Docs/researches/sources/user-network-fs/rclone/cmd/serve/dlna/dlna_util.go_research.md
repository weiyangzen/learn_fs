# sources/user-network-fs/rclone/cmd/serve/dlna/dlna_util.go

## Purpose

This utility file provides naming, UUID generation, interface filtering, DIDL/SOAP XML helpers, request logging, trace logging, response headers, error handling, and extension splitting for the DLNA server.

## Important APIs, Types, and Functions

Important functions include `makeDefaultFriendlyName`, `makeDeviceUUID`, `listInterfaces`, `isAppropriatelyConfigured`, `didlLite`, `adjustXML`, `mustMarshalXML`, `soapArgs`, `marshalSOAPResponse`, `logging`, `traceLogging`, `withHeader`, `serveError`, and `splitExt`. `soapArg` preserves SOAP argument order.

## Control Flow

HTTP middleware wraps handlers with panic/error logging and optional full request/response dumping. SOAP output marshals args in explicit slice order, then replaces numeric XML entities for compatibility before wrapping them in an action response. Interface helpers filter usable SSDP interfaces.

## State and Persistence Behavior

No durable state is stored. `loggingResponseWriter` tracks per-request commit state, and trace logging buffers the response through `httptest.ResponseRecorder`.

## Dependencies and Integration Points

Utilities are used across `dlna.go` and `cds.go`, and depend on rclone logging, anacrolix SOAP/UPnP, net interfaces, HTTP test utilities, and XML encoding.

## Risks and Test Signals

Risks include response buffering memory cost under trace logging, panic recovery after partial response commit, `maps.Copy` header behavior for multi-value headers, and fragile XML string substitutions. Tests cover XML entity adjustment, SOAP quote escaping, and ordered Browse response output.
