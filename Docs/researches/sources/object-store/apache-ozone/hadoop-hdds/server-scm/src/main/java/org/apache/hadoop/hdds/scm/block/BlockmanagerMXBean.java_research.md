# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockmanagerMXBean.java

Purpose: Marker JMX management interface for `BlockManagerImpl`.

Important APIs and types: Empty interface implemented by `BlockManagerImpl`, which registers with Hadoop `MBeans`.

Control flow: Participates in MBean registration but currently exposes no explicit management attributes or operations.

State and persistence behavior: No state or persistence.

Dependencies and integration points: JMX/Hadoop MBeans integration point for future block-manager management data.

Risks: Empty MBean has limited operational value; adding methods later changes management API surface.

Test signals: Lifecycle tests should confirm MBean registration and unregistration do not leak.
