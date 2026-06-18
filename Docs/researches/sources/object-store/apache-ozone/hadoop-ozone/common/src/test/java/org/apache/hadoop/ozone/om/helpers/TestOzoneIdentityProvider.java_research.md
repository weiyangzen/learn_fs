# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneIdentityProvider.java

Purpose: tests `OzoneIdentityProvider` identity extraction from IPC `Schedulable` requests, preferring trusted S3 caller context when present.

Important APIs/types/functions: exercises `OzoneIdentityProvider.makeIdentity`, `Schedulable.getUserGroupInformation`, optional `getCallerContext`, and `OM_S3_CALLER_CONTEXT_PREFIX`.

Control flow and state: three schedulables model default UGI-only requests, S3 gateway requests with a prefixed caller context, and requests with an untrusted/non-prefixed caller context. The provider returns the access ID from prefixed context, otherwise falls back to UGI short username.

Dependencies and integration points: uses Hadoop IPC `CallerContext`, `Schedulable`, and `UserGroupInformation`. It integrates with OM scheduling/identity attribution and S3 gateway caller propagation.

Risks and test signals: protects against trusting arbitrary caller context, failing when default schedulable throws `UnsupportedOperationException` for caller context, and losing S3 end-user identity behind the gateway principal.
