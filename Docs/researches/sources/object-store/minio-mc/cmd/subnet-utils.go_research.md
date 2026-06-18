# sources/object-store/minio-mc/cmd/subnet-utils.go

## Purpose
Provides shared SUBNET support utilities: URL builders, authentication headers, HTTP request helpers, debug redaction, MinIO server config lookup/mutation for SUBNET keys, mc config fallback, cluster registration metadata, login/MFA flows, credential exchange, license validation, upload URL preparation, and connectivity initialization.

## Important APIs, types, and functions
- URL helpers: `SubnetBaseURL`, `subnetIssueURL`, `SubnetUploadURL`, `SubnetRegisterURL`, unregister/license/login/API key/MFA URL builders.
- HTTP helpers: `checkURLReachable`, `subnetReqDo`, `subnetHeadReq`, `subnetGetReq`, `SubnetPostReq`, `subnetHTTPDo`, `dumpHTTPReq`.
- Auth helpers: `SubnetHeaders`, `addDeploymentIDHeader`, token/license/API-key header builders, `subnetURLWithAuth`.
- Config helpers: `getMinIOSubSysConfig`, `getMinIOSubnetConfig`, `getKeyFromSubnetConfig`, `getSubnetAPIKeyFromConfig`, `getSubnetLicenseFromConfig`, `setGlobalSubnetProxyFromConfig`, `mcConfig`, `setSubnetAPIKey`, `setSubnetLicense`, and lower-level config setters.
- Registration helpers: `GetClusterRegInfo`, `getDriveSpaceInfo`, `generateRegToken`, `registerClusterOnSubnet`, `unregisterClusterFromSubnet`, `removeSubnetAuthConfig`.
- Credential helpers: `subnetLogin`, `getSubnetCreds`, `getSubnetAPIKey`, API-key/license exchange functions, `extractAndSaveSubnetCreds`, `extractSubnetCred`, `parseLicense`, `validateAndSaveLic`.
- Command helpers: `prepareSubnetUploadURL`, `getAPIKeyFlag`, `initSubnetConnectivity`.

## Control flow
SUBNET commands typically call `initSubnetConnectivity`, which validates `--airgap`/`--api-key`, extracts alias, parses UUID API key, applies proxy config unless airgapped, and checks SUBNET base URL reachability when requested. Commands needing upload URLs call `prepareSubnetUploadURL`, which resolves an API key from flag/config/login if necessary and returns authenticated request URL/headers.

HTTP requests go through `subnetReqDo`, which adds headers, defaults content type to JSON, executes via a proxy-aware client, optionally dumps redacted debug HTTP, limits response body to 1 MiB, and treats only HTTP 200 as success.

Credential resolution first checks MinIO server `subnet` subsystem config when supported, otherwise falls back to local mc alias config. If only API key or license is present and not airgapped, it attempts to fetch and save the missing credential. Registration posts a base64-encoded cluster registration token to SUBNET and saves returned license/API key.

## State and persistence
State surfaces include:
- Global process state: `globalSubnetConfig` cache, `GlobalSubnetProxyURL`, `globalAirgapped`, `GlobalDevMode`, `globalDebug`.
- Remote MinIO server config: `subnet api_key`, `subnet license`, and proxy values via admin config APIs.
- Local mc config alias fields: API key and license fallback.
- Interactive terminal input for login/MFA.
No arbitrary files are written directly here; config mutations go through established config/admin APIs.

## Dependencies and integration points
Integrates with MinIO admin APIs (`GetConfigKV`, `SetConfigKV`, `HelpConfigKV`, admin info), SUBNET package base URL and license validator, `madmin.InfoMessage`, `gjson`, `uuid`, terminal password input, HTTP client/proxy helpers, local config loading/saving, and support/license commands.

## Risks and edge cases
- `subnetReqDo` accepts only status 200; APIs returning 201/204 would be treated as failures.
- Debug dumping redacts sensitive headers but uses `query.Add` instead of replacing existing query secrets, which can leave original query values in the dump.
- `extractSubnetCred` treats `result.Index == 0` as missing; a top-level field at byte index 0 could be misdetected depending on gjson behavior, though object fields usually have nonzero indexes.
- `GetClusterRegInfo` indexes `admInfo.Servers[0]` and assumes at least one server.
- `getSubnetCreds` can perform network calls and config writes as a side effect of a credential read.
- `removeSubnetAuthConfig` always writes server config, not local fallback, which may not clear locally stored credentials on older/non-supporting targets.

## Test signals
`subnet-utils_test.go` checks that `SubnetBaseURL` parses as an HTTPS URL. More tests are needed for URL construction, HTTP status handling, redaction, credential extraction, config fallback, registration token generation, and airgap/proxy behavior.
