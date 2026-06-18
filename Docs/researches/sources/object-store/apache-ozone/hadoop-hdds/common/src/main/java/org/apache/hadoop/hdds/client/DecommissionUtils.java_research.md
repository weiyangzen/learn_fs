## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/DecommissionUtils.java

Purpose: stateless helpers for decommission status filtering and parsing datanode metrics JSON.

Important APIs: `getDecommissioningNodesList` filters streamed node protos by UUID, IP address, or returns all; `getBeansJsonNode` parses metrics JSON and returns the first `beans` element; `getNumDecomNodes` reads `DecommissioningMaintenanceNodesTotal`; `getCountsMap` scans indexed metrics fields for a datanode hostname and populates decommission start time, unclosed pipeline count, under-replicated container count, and unclosed container count.

Control flow: filter preference is UUID first, then IP, then all. Metrics parsing assumes JMX-style `beans[0]` and numbered per-datanode metric keys. State/persistence: no state; caller-supplied map is mutated.

Dependencies: Jackson JSON, Guava `Strings`, `DatanodeDetails`, HDDS protos, Java date formatting. Integration points: CLI/admin decommission status commands and Recon/SCM metrics display. Risks: brittle JSON shape assumptions; hostname matching ignores IP/UUID; default timezone in `SimpleDateFormat` can make output environment-dependent; numeric parsing from `JsonNode.toString()` is fragile compared with `asInt/asLong`. Test signals: metrics JSON with missing fields, zero nodes, hostname mismatch, UUID/IP filter precedence, timezone-sensitive formatting, and malformed JSON.
