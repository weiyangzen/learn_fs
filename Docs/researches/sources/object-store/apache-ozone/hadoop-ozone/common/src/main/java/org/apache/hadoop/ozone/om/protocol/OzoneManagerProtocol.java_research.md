<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerProtocol.java

## Purpose

`OzoneManagerProtocol` is the main Java client/server contract for OM metadata operations. It spans volume, bucket, key, multipart upload, S3 secret, tenant, snapshot, filesystem, ACL, DB update, prepare, lease, safe mode, tagging, quota repair, and upgrade-finalization APIs.

## Important APIs, Types, And Functions

The interface extends `IOmMetadataReader`, `OzoneManagerSecurityProtocol`, and `Closeable`, and carries Kerberos/token annotations. Abstract read-style methods include volume/bucket listing and info, key lookup/info, service discovery, open-file listing, tenant reads, list status, DB updates, echo RPC, lease recovery, safe mode, object tagging read, and quota repair status. Many write APIs are default methods throwing `UnsupportedOperationException` because write requests use newer request-submission paths.

## Control Flow, State, And Persistence

This file defines protocol shape rather than implementation. Implementations route read methods directly and write methods through OM request/Ratis paths. The API exposes pagination tokens, snapshot diff jobs, prepare-state queries, upgrade progress, and DB update streams; durable state lives in OM metadata tables, Ratis logs, delegation token state, snapshot checkpoints, tenant tables, and secret tables.

## Dependencies And Integration Points

It depends on nearly every common OM helper model plus HDDS SCM allocation types, ACLs, protobuf response/request types, snapshot response types, upgrade finalization, safe mode, and security token annotations. It integrates with client-side translators, server-side translators, S3 gateway, OzoneFS, admin/CLI tooling, Recon/DB sync, HA failover, and OM metadata readers.

## Risks And Test Signals

The interface mixes old direct methods with newer default unsupported write methods; translators must choose the correct path. Tests should cover every translator mapping, unsupported defaults, pagination boundaries, tenant/snapshot/multipart flows, follower-read consistency, prepare/finalize transitions, DB update streaming, safe mode actions, ACL/tagging semantics, and backward compatibility for deprecated methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerProtocol.java -->
