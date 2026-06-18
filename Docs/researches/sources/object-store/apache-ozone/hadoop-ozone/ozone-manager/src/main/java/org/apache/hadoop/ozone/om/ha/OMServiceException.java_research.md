# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMServiceException.java

Purpose: `OMServiceException` is the checked exception type used by `OMService.start()`.

Important APIs and types: It extends `Exception` and provides default, message, message-plus-cause, and cause-only constructors.

Control flow: There is no custom control flow.

State and persistence behavior: It carries exception state only and persists nothing.

Dependencies and integration points: `OMServiceManager.start` catches this exception and logs a warning while continuing with other services.

Risks and test signals: This is straightforward. Tests should verify service manager catches it and does not prevent later services from starting.
