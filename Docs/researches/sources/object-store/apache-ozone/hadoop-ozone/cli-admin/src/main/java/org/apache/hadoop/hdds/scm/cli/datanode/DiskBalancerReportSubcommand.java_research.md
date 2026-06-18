# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerReportSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer report`, retrieving volume-density and per-volume usage reports from one or more datanodes.

## Important APIs, Types, And Functions
Extends `AbstractDiskBalancerSubCommand`; `executeCommand` creates a `DiskBalancerProtocol` proxy and calls `getDiskBalancerInfo`. `generateReport` formats `DatanodeDiskBalancerInfoProto` and `VolumeReportProto`; `toJson` builds JSON maps with density, ideal usage, threshold range, and volume rows.

## Control Flow
For each target datanode, it fetches disk balancer info and either returns a JSON map or stores the proto in a concurrent map. After all targets, non-JSON mode prints failures and a report sorted by aggregate density descending.

## State And Persistence
Read-only against datanode DiskBalancer state. It caches fetched protos for consolidated output.

## Dependencies And Integration Points
Depends on datanode `DiskBalancerProtocol`, protobuf disk/volume reports, `DiskBalancerSubCommandUtil`, and Hadoop `StringUtils.byteDesc`.

## Risks And Test Signals
Formatting uses a dynamic `String.format` template and content list; mismatches could throw. Tests should cover nodes with no ideal usage, no volumes, failed nodes, JSON output, display name formatting, and percent calculations.
