<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneDelegationTokenRenewer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneDelegationTokenRenewer.java

## Purpose
Hadoop token renewer for Ozone delegation tokens.

## Important APIs, types, and functions
Extends `TokenRenewer`. `getKind` returns `OzoneTokenIdentifier.KIND_NAME`; `handleKind` matches that kind; `isManaged` returns true. `renew` and `cancel` cast the token, build an `OzoneConfiguration`, open an `OzoneClient` with the token, and call object-store token renewal/cancel APIs.

## Control flow
A static initializer activates Ozone configuration resources. Each renew/cancel operation opens a short-lived authenticated client in a try-with-resources block and delegates to OM through the object store.

## State and persistence behavior
No state is retained. Renewal extends token validity in OM security state; cancel invalidates it.

## Dependencies and integration points
Integrates Hadoop token lifecycle services, Ozone client factory, `OzoneConfiguration`, `OzoneTokenIdentifier`, and OM token management.

## Risks and test signals
Incorrect token kind handling or missing config activation would break long-running secure jobs. Tests should cover kind matching, successful renew/cancel with a mocked or mini-cluster OM, and propagation of IO failures from the object store.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneDelegationTokenRenewer.java -->
