# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMServiceException.java

Purpose: Checked exception type used by `SCMService.start` to report service startup failures.

Important APIs and types: Provides the standard constructors: no-arg, message, message-with-cause, and cause-only.

Control flow: `SCMServiceManager.start` catches this exception per service, logs a warning, and continues starting other services.

State and persistence behavior: No state beyond standard `Exception` message/cause fields and no persistence behavior.

Dependencies and integration points: Couples background service implementations to the service manager without forcing unchecked startup failure.

Risks and test signals: Because the manager logs and continues, a service can fail to start without failing SCM startup. Tests should assert that exceptions preserve cause/message and that manager-level startup proceeds to later services after one service throws.
