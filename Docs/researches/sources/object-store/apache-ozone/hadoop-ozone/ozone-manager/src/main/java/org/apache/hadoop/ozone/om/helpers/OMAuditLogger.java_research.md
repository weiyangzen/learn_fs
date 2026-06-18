# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/OMAuditLogger.java

Purpose: `OMAuditLogger` centralizes mapping OM request command types to audit actions and provides helper methods for writing audit log messages during request execution and failure handling.

Important APIs and types: Static `CMD_AUDIT_ACTION_MAP` maps protobuf `Type` to `OMAction`. Public `log` overloads write an already-built builder, add transaction index, or build audit data from an `OMClientRequest`, `OzoneManager`, `TermIndex`, and throwable. `Builder` holds `AuditMessage.Builder`, `AuditLogger`, audit params, and an `AtomicBoolean` log flag.

Control flow: Static initialization populates the command-action map. `getAction` special-cases `SetVolumeProperty` quota updates and `SetBucketProperty` owner updates. The request-aware `log` method either writes an already-prepared message or maps command to action, populates command and transaction parameters, asks the client request to build the audit message, marks the builder as logged, and writes through OM's audit logger.

State and persistence behavior: Static mapping is process state. Audit persistence is external to this class through the configured audit logger sink.

Dependencies and integration points: It is used by OM request execution, Ratis application, and failure paths. It depends on `AuditLogger`, `AuditMessage`, `OMAction`, protobuf command types, and `OMClientRequest`.

Risks and test signals: Missing map entries silently suppress audit logs. Builder state is mutable and can be reused incorrectly. Tests should cover every auditable command mapping, quota/owner special cases, transaction parameter insertion, already-logged short circuit, exception handling during audit message construction, and no log for unmapped commands.
