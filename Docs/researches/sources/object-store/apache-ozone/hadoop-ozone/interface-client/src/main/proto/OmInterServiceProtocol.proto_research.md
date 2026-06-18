# sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OmInterServiceProtocol.proto

Purpose: Private unstable protobuf/gRPC protocol for OM-to-OM communication in HA setups, focused on bootstrapping a new OM into an existing OM ring.

Important APIs/types/functions: Generates `OzoneManagerInterServiceProtocolProtos`. Defines `BootstrapOMRequest` with node id, host address, Ratis port, and listener flag; `BootstrapOMResponse` with success, optional `ErrorCode`, and error message; `ErrorCode` values for Ratis disabled, leader undetermined/not ready, bootstrap error, and undefined error; service `OzoneManagerInterService.bootstrap`.

Control flow, state, and persistence: The protocol describes a coordination step where a joining OM contacts an existing OM service to bootstrap HA metadata/Ratis membership. It does not persist state itself, but request handling updates OM HA membership and depends on Ratis state.

Dependencies and integration points: Generated stubs are used by OM HA bootstrap/admin workflows. It integrates with OM Ratis membership, leader readiness checks, and listener/non-voting OM mode.

Risks: Bootstrap is cluster-membership sensitive. Misinterpreting `isListener` or leader readiness can create invalid HA topology or failed joins. Required fields mean old/new clients must supply node identity and Ratis address.

Test signals: Expected downstream coverage is OM HA bootstrap integration tests. The proto compatibility plugin should guard field-number changes.
