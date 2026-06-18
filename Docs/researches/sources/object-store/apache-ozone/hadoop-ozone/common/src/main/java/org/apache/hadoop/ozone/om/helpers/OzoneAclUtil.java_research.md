<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclUtil.java

## Purpose

`OzoneAclUtil` centralizes ACL helper logic for OM metadata objects: default ACL creation, filtering, access checks, default ACL inheritance, protobuf conversion, and list mutation.

## Important APIs, Types, And Functions

Key methods are `getDefaultAclList`, `getAclList`, `filterAclList`, `checkAclRights`, `inheritDefaultAcls`, `fromProtobuf`, `toProtobuf`, `addAcl`, `addAllAcl`, `removeAcl`, and `setAcl`. `checkAccessInAcl` implements user/group/other matching against `RequestContext`.

## Control Flow, State, And Persistence

The class is stateless. Default ACL methods build new lists from UGI and OM default-right configuration. Mutation methods operate in place on supplied lists, merging ACL bitsets for matching identity/type/scope and removing empty entries. Persistence occurs when mutated ACL lists are serialized by volume, bucket, or key metadata classes.

## Dependencies And Integration Points

It depends on `OzoneAcl`, `OmConfig`, `IAccessAuthorizer`, `RequestContext`, UGI, and ACL protobufs. It is used by volume/bucket/key builders, authorization checks, default ACL inheritance during directory/key creation, and protocol translators.

## Risks And Test Signals

The raw `List retList` in `filterAclList` loses generic type safety. Group lookup failures are logged but do not fail default ACL creation. Tests should cover ACL merge/remove semantics, `ALL` and `NONE` behavior through `OzoneAcl.checkAccess`, default ACL inheritance with scope conversion, protobuf round trips, and user primary-group lookup failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclUtil.java -->
