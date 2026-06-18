# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/RangerUserRequest.java

## Purpose
Test helper for creating, querying, and deleting Apache Ranger users through Ranger Admin REST endpoints because the Ranger client used by Ozone tests does not provide those user-management APIs.

## Important APIs and Types
The helper class `RangerUserRequest` exposes `getUserId`, `createUser`, and `deleteUser`. Internal methods include `setupRangerIgnoreServerCertificate`, `openURLConnection`, `makeHttpCall`, `makeHttpGetCall`, `getCreateUserJsonStr`, and `getResponseData`. It uses `HttpURLConnection`, `HttpsURLConnection`, custom `X509TrustManager`, `SSLContext`, Ozone Ranger endpoint constants, `JsonUtils`, Jackson `JsonNode`, and Kerby `Base64`.

## Control Flow
Construction normalizes the Ranger endpoint, builds a Basic authorization header, and installs a permissive default HTTPS socket factory. Calls open HTTP or HTTPS connections, set method, timeouts, JSON headers, authorization, and optional request body. `createUser` posts generated JSON and parses the returned `id`; `getUserId` reads the Ranger user search/list response and scans `vXUsers` for the requested principal; `deleteUser` sends a force-delete request and accepts HTTP 200 or 204.

## State and Persistence
Runtime state is the Ranger endpoint, Basic auth header, and timeout values. Durable effects are external Ranger user records created or deleted via REST. The helper also mutates JVM-wide HTTPS default socket factory, which persists beyond one instance.

## Dependencies and Integration Points
It supports multitenancy Ranger sync integration tests, bridging Ozone test code to Ranger Admin user endpoints. It relies on Ozone constants for endpoint paths and Ranger's JSON response schema.

## Risks and Edge Cases
The permissive trust manager disables certificate validation process-wide for `HttpsURLConnection`, acceptable only in controlled integration tests. JSON request bodies are manually concatenated and do not escape usernames/passwords. `isSpnego` parameters are unused. Error handling logs some 400/401 cases but can return null response data, and Java `assert userInfo != null` is ineffective unless assertions are enabled.

## Test Signals
This file is helper infrastructure, not a test class. Its signals are indirect: Ranger sync tests can create cleanup users, resolve user IDs, and remove users after policy/role reconciliation checks.
