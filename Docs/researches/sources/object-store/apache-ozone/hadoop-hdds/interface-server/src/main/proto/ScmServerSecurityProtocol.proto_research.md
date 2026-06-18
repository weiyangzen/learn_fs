<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerSecurityProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerSecurityProtocol.proto

## Purpose

Defines the SCM security service for certificate signing, certificate retrieval, CRL lookup, datanode/OM certificate renewal, and token or secret related security material exchange.

## Important APIs, types, and functions

Package: `hadoop.hdds.security`. Imports: `hdds.proto`. Important declarations include `SCMSecurityRequest, SCMSecurityResponse, SCMGetDataNodeCertRequestProto, SCMGetOMCertRequestProto, SCMGetCertRequestProto, SCMGetSCMCertRequestProto, SCMGetCertificateRequestProto, SCMGetCACertificateRequestProto, SCMListCertificateRequestProto, SCMGetCertResponseProto, SCMListCertificateResponseProto, SCMGetAllRootCaCertificatesResponseProto, SCMRemoveExpiredCertificatesResponseProto, SCMGetRootCACertificateRequestProto, SCMListCACertificateRequestProto, SCMGetCrlsRequestProto, SCMGetCrlsResponseProto, SCMGetLatestCrlIdRequestProto, SCMGetLatestCrlIdResponseProto, SCMRevokeCertificatesRequestProto, SCMGetAllRootCaCertificatesRequestProto, SCMRevokeCertificatesResponseProto, SCMRemoveExpiredCertificatesRequestProto, Type, Status, ResponseCode, ResponseCode, Reason, ...`. RPC methods: submitRequest(SCMSecurityRequest -> SCMSecurityResponse).

## Control flow

Requests are wrapped in SCMGetCertRequestProto or service-specific request messages and served through a protobuf RPC service. Responses carry PEM/certificate material, CRL IDs and lists, and status/error information.

## State and persistence behavior

This file does not persist state directly. It defines the wire schema consumed by generated protobuf classes and by SCM, datanode, client, or IPC implementations. Persistent effects happen in the managers that handle the generated request objects, such as SCM metadata stores, datanode container stores, Ratis logs, certificate stores, and runtime configuration managers.

## Dependencies and integration points

The generated Java package integrates with Maven protobuf generation in the interface modules. Shared messages imported from `hdds.proto` connect this protocol to node identity, pipeline, container, token, replication, disk-balancer, and report models. Service declarations integrate with Hadoop/Ratis protobuf RPC stubs.

## Risks and edge cases

Security risk is high: CSR validation, identity binding, serial/CRL monotonicity, and authorization are enforced outside the proto but are required for safe use. Wire compatibility must preserve certificate and CRL fields exactly.

## Test signals

Strong tests should include protobuf backward-compatibility checks, generated-service compile checks, request/response round trips with absent optional fields, unknown enum handling where possible, and integration tests in the SCM/datanode/server modules that exercise each command type against real managers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-server/src/main/proto/ScmServerSecurityProtocol.proto -->
