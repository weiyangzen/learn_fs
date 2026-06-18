<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/S3Auth.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/S3Auth.java

## Purpose

`S3Auth` carries S3 signature authentication data from gateway/client layers to OM request handling.

## Important APIs, Types, And Functions

The class stores the string-to-sign, signature, access ID, and user principal. It exposes getters and a setter for `userPrincipal`, which can be filled after access ID resolution.

## Control Flow, State, And Persistence

Instances are transient per-request authentication context. OM or gateway code resolves the access ID to a user principal and may place this object in thread-local client protocol state. It is not persisted.

## Dependencies And Integration Points

It integrates with `OzoneManagerClientProtocol` thread-local S3 auth, S3 secret lookup, request signing, and `OzoneIdentityProvider` caller-context attribution.

## Risks And Test Signals

The object is mutable only for user principal, so thread-local cleanup is critical. Tests should cover signature/access ID propagation, principal resolution, failed auth, thread-local clear behavior, and concurrent S3 requests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/S3Auth.java -->
