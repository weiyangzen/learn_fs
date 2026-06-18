# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/ListSubcommand.java

## Purpose
Implements `ozone admin cert list`, listing SCM-issued certificates by role with text or JSON formatting.

## Important APIs, Types, And Functions
Options include `--start`, `--count`, `--role`, deprecated `--type`, and `--json`. `parseCertRole` maps `om`, `scm`, and other values to `HddsProtos.NodeType`. `execute` calls `SCMSecurityProtocol.listCertificate`, warns when the batch is full, and formats PEMs. Nested `Certificate` parses `X509Certificate` into serial, validity, subject DN, and issuer DN maps.

## Control Flow
The command chooses node type, fetches up to `count` certificates from `startSerialId`, then either prints tabular PEM-derived rows through `printCertList` or serializes parsed DTOs as JSON.

## State And Persistence
It is read-only against SCM certificate state.

## Dependencies And Integration Points
Depends on SCM security RPCs, `CertificateCodec`, Jackson serializers, `JsonUtils`, and `ScmCertSubcommand`.

## Risks And Test Signals
Unrecognized roles silently default to datanode. DN parsing splits on commas and equals signs and may mis-handle escaped DN components. Tests should cover role mapping, full-batch warning, JSON parse failures, deprecated option compatibility, and large serial values.
