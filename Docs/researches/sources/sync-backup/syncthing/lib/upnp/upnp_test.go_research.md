# sources/sync-backup/syncthing/lib/upnp/upnp_test.go

Purpose: unit tests for UPnP SOAP XML parsing and control URL normalization.

Important tests: `TestExternalIPParsing` unmarshals a SOAP external-IP response and expects `1.2.3.4`. `TestSoapFaultParsing` unmarshals a UPnP fault and expects error code 725. `TestControlURLParsing` verifies `replaceRawPath` produces the expected control URL for absolute-path and absolute-URL inputs.

State and persistence: no state; static XML and URL strings.

Dependencies and integration: covers internal response structs used by `IGDService.GetExternalIPv4Address` and error handling in port mapping/pinhole paths.

Risks and signals: helpful for XML tag paths and URL handling. It does not test SSDP sockets, device-description parsing, SOAP HTTP transport, IPv6 link-local handling, or actual NAT operations.
