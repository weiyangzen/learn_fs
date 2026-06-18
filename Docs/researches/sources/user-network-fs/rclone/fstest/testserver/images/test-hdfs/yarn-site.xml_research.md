
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/yarn-site.xml

Purpose: YARN timeline/logging configuration included in the HDFS test image.

Important APIs/types/functions: enables log aggregation and timeline service, configures shuffle service, binds node manager/timeline service to all interfaces, and sets remote app log/timeline paths.

Control flow: declarative XML consumed by Hadoop/YARN services.

State/persistence: refers to `/app-logs` and `/hadoop/yarn/timeline` paths inside the container.

Dependencies/integration: copied by Dockerfile; supports Hadoop config completeness more than rclone core behavior.

Risks: duplicate `yarn.nodemanager.bind-host` appears; harmless but noisy. Timeline hostname is fixed to `historyserver.hadoop`.

Test signals: config-load success; rclone HDFS tests do not directly validate YARN behavior.
