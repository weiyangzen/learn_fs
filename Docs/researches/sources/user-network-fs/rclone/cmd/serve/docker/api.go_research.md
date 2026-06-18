# sources/user-network-fs/rclone/cmd/serve/docker/api.go

## Purpose

`api.go` exposes the Docker volume plugin HTTP API and adapts JSON requests to the driver methods.

## Important APIs, Types, and Functions

It defines request/response structs for create, remove, mount, unmount, path, get, list, capabilities, and errors. `newRouter` registers chi POST routes for Docker plugin endpoints. `decodeRequest` decodes JSON; `encodeResponse` writes Docker plugin content type, success bodies, or `ErrorResponse`.

## Control Flow

Each route decodes the JSON body into a typed request, calls the corresponding `Driver` method, and encodes either the response or an HTTP 500 error JSON understood by Docker. `/Plugin.Activate` returns `Implements: ["VolumeDriver"]`; capabilities returns the configured scope.

## State and Persistence Behavior

The router itself is stateless; all volume state lives in `Driver`.

## Dependencies and Integration Points

It depends on Docker's plugin HTTP contract, chi routing, rclone logging, and the driver/volume types in this package.

## Risks and Test Signals

Risks include returning HTTP 500 for all driver errors, no method/content negotiation beyond route matching, and limited decode error format. `docker_test.go` exercises activation and create/mount/unmount/remove/list API flows over TCP and Unix sockets when enabled.
