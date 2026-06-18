<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/O3fsDtFetcher.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/O3fsDtFetcher.java

## Purpose
Delegation-token fetcher for the `hadoop dtutil` command and the `o3fs` URL scheme.

## Important APIs, types, and functions
Implements Hadoop `DtFetcher`. `getServiceName` returns the Ozone URI scheme, `isTokenRequired` mirrors Hadoop security state, and `addDelegationTokens` creates a `FileSystem`, fetches a delegation token, adds it to `Credentials`, and returns it.

## Control flow
If the supplied URL lacks the `o3fs` prefix, it prepends `o3fs://`. It then opens the filesystem for that URI, calls `getDelegationToken(renewer)`, fails with `IOException` if no token is returned, and stores the token under its service.

## State and persistence behavior
No local state is persisted. The observable mutation is adding the token to the provided credentials object.

## Dependencies and integration points
Integrates Hadoop security, `FileSystem.get`, `Credentials`, `Token`, and Ozone delegation token implementation. It is service-loaded by Hadoop tooling rather than called by filesystem paths directly.

## Risks and test signals
Bad URL normalization or null token handling would break secure job submission and dtutil workflows. Tests should exercise prefixed and unprefixed URLs, secure vs insecure mode, token insertion, and failure when the filesystem returns null.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/O3fsDtFetcher.java -->
