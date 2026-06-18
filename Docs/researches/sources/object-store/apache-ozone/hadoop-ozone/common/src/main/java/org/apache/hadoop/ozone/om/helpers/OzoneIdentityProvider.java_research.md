<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneIdentityProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneIdentityProvider.java

## Purpose

`OzoneIdentityProvider` supplies identity strings to Hadoop's decay RPC scheduler. It prefers OM-provided S3 caller context over raw RPC user identity so S3 gateway traffic can be attributed to the authenticated S3 principal.

## Important APIs, Types, And Functions

The only behavior is `makeIdentity(Schedulable)`. It reads UGI, attempts to read `CallerContext`, checks for `OM_S3_CALLER_CONTEXT_PREFIX`, and otherwise returns the UGI short user name.

## Control Flow, State, And Persistence

The class is stateless. If the schedulable implementation does not support caller context, it logs an error and falls back to UGI. No state is persisted; the returned identity affects runtime scheduling and fairness.

## Dependencies And Integration Points

It depends on Hadoop `IdentityProvider`, `Schedulable`, `CallerContext`, UGI, and Ozone S3 caller-context constants. It integrates with OM RPC server scheduling, especially S3 gateway requests where the gateway service user differs from the end user.

## Risks And Test Signals

Only caller contexts with the trusted OM prefix are accepted; user-supplied contexts are ignored. Tests should cover S3-prefixed context, non-prefixed context, null context, unsupported schedulable implementations, and null short user names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneIdentityProvider.java -->
