# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRestInterface.java

## Purpose
Abstract non-HA integration test for the Ozone Manager HTTP `/serviceList` endpoint. It validates that OM exposes discoverable service metadata for OM and SCM through its embedded HTTP server.

## Important APIs and Types
The file defines `TestOzoneManagerRestInterface`, implementing `NonHATests.TestCase`. Important members are `setup` and `testGetServiceList`. It uses `OzoneManagerHttpServer`, Apache `HttpClient`/`HttpGet`, Jackson `ObjectMapper`, `ServiceInfo`, `HddsProtos.NodeType`, `ServicePort.Type`, `OmUtils.getOmRpcAddress`, and `HddsUtils.getScmAddressForClients`.

## Control Flow
`@BeforeAll` caches the provided mini-cluster and configuration. The test builds an HTTP URL from the OM HTTP server address, performs `GET /serviceList`, parses the JSON response as `List<ServiceInfo>`, maps entries by node type, and compares returned host/port values with the configuration and live HTTP server address.

## State and Persistence
There is no local persistence. The endpoint reflects runtime service registration state from the running mini-cluster. The test reads configuration-derived OM and SCM addresses and HTTP/RPC ports from the response.

## Dependencies and Integration Points
This is an integration boundary between OM's HTTP server, JSON serialization of service discovery data, client-side service metadata types, and SCM address configuration.

## Risks and Edge Cases
The test assumes exactly one relevant SCM client address is available from the iterator and that host-name formatting matches `ServiceInfo`. It does not assert HTTP status before parsing, nor does it validate optional service entries beyond OM and SCM.

## Test Signals
Passing indicates `/serviceList` produces valid JSON consumable as `ServiceInfo`, includes OM and SCM entries, and advertises correct OM RPC/HTTP and SCM RPC addresses.
