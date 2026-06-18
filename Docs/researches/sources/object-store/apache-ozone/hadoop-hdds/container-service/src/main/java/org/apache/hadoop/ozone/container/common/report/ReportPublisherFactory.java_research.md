<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisherFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisherFactory.java

Purpose: maps protobuf report classes to concrete `ReportPublisher` implementations.

Important APIs and control flow: constructor stores configuration and initializes a map for `NodeReportProto`, `ContainerReportsProto`, `CommandStatusReportsProto`, and `PipelineReportsProto`. `getPublisherFor` looks up the publisher class, throws when no mapping exists, instantiates it reflectively with a no-arg constructor, injects config, and returns it.

State and persistence: in-memory immutable-ish mapping after construction. No persistence.

Dependencies and integration: used by `ReportManager.Builder.addPublisherFor` during datanode report manager assembly.

Risks and test signals: tests should cover all known mappings, unknown report class failures, configuration injection, and reflection failure if a publisher lacks a public no-arg constructor. `Class.newInstance` is deprecated and wraps failures broadly, so error messages may be less precise.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisherFactory.java -->
