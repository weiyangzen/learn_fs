<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/mountinterface.go -->
# sources/user-network-fs/go-nfs/mountinterface.go

## Purpose
Defines mount protocol constants, enum stringers, auth flavor constants, and mount request/response shapes.

## Important APIs, Types, and Functions
Important declarations are service ID companion values, `FHSize`, `MNTNameLen`, `MountStatus`, `MountProcedure.String`, `AuthFlavor`, `MountRequest`, and `MountResponse`.

## Control Flow
No runtime control flow except enum string conversion.

## State and Persistence Behavior
Stateless protocol definitions.

## Dependencies and Integration Points
Used by `mount.go`, handler implementations, and request logging.

## Risks and Edge Cases
Constants must match RFC/NFS mount protocol expectations. `MountResponse.AuthFlavors` uses `[]int` while auth flavor constants are typed, so encoding assumptions matter.

## Test Signals
Mount procedure tests and client mount attempts validate the wire shape.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/mountinterface.go -->
