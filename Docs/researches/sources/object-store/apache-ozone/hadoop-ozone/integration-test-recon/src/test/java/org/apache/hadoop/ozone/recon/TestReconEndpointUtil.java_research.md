# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconEndpointUtil.java

## Purpose

This utility class centralizes HTTP access to Recon endpoints for integration tests. It builds the correct Recon web base URL from Ozone configuration, triggers the OM DB sync endpoint, fetches unhealthy-container JSON, and normalizes HTTP/HTTPS address handling.

## Important APIs, types, and functions

The main methods are `triggerReconDbSyncWithOm()`, `getUnhealthyContainersFromRecon()`, `makeHttpCall()`, `getReconWebAddress()`, `getHostOnly()`, `getPort()`, and `isHTTPSEnabled()`. It uses `URLConnectionFactory`, `HttpURLConnection`, Jackson `ObjectMapper`, `UnhealthyContainersResponse`, and Recon configuration keys for RPC, HTTP, and HTTPS addresses.

## Control flow, state, and persistence

The class is stateless. `triggerReconDbSyncWithOm()` calls `/api/v1/triggerdbsync/om` and logs failures if the response is not `true`. `getUnhealthyContainersFromRecon()` calls `/api/v1/containers/unhealthy/{state}` and deserializes the response body. `makeHttpCall()` opens a URL connection, optionally with SPNEGO when HTTPS-only is configured, returns payloads for HTTP 200/201, and returns null on initialization or refused-connection cases.

## Dependencies and integration points

It integrates test code with Recon's REST API and with Hadoop HTTP policy configuration. `getReconWebAddress()` uses the configured HTTP or HTTPS bind address but falls back to the Recon RPC hostname when the web host remains at its default wildcard host. This matters in mini-cluster tests where bind addresses often use `0.0.0.0` but clients need a reachable host.

## Risks and test signals

The helpers swallow several exceptions and return null or log only, so caller tests may fail later during JSON parsing rather than at the original connection failure. `getHostOnly()` and `getPort()` split on the first colon and are not IPv6-safe. Positive test signals are successful sync trigger responses, valid unhealthy-container JSON deserialization, and correct URL construction for HTTP and HTTPS policies.
