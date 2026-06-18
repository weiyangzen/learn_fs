# sources/object-store/minio/cmd/net_test.go

This file unit-tests the network helper behavior from `net.go`. It focuses on address parsing, local endpoint formatting, IP sorting, local-host validation, and IP literal detection.

`TestMustSplitHostPort` verifies numeric ports and service names such as `https` and `http`. `TestSortIPs` checks hostname preservation, loopback demotion, and last-octet sorting across mixed inputs. `TestMustGetLocalIP4` and `TestGetHostIP` assert that localhost resolves to a usable loopback address. `TestGetAPIEndpoints` temporarily mutates `globalMinioHost` and `globalMinioPort` to verify rendered API endpoints. `TestCheckLocalServerAddr` covers wildcard, localhost, empty, remote, and invalid port inputs. `TestExtractHostPort`, `TestSameLocalAddrs`, and `TestIsHostIP` cover URL-like, bare host/port, empty, remote, and IPv6-zone forms.

State mutation is limited but important: `TestGetAPIEndpoints` saves and restores globals. Other tests depend on host DNS and local interface behavior, so they may be environment-sensitive. Dependencies include `testing`, `reflect`, MinIO string sets, and real network lookup through production helpers.

Risks: tests assume `localhost` intersects with `127.0.0.1`, which is common but still environment-dependent. They do not cover dynamic interface changes, IPv6 endpoint rendering in detail, or DNS cache failure injection. The suite is still a useful guard for startup address UX.
