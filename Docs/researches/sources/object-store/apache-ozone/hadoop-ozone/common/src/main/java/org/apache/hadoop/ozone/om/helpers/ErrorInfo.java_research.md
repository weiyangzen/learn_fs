# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ErrorInfo.java

Purpose: Simple mutable error DTO containing an error code and message.

Important APIs/types/functions: Constructor, getters, and setters for `code` and `message`.

Control flow and state: No control flow. Both fields are mutable.

State and persistence behavior: No persistence behavior in this class. It is suitable for API/response error payloads.

Dependencies and integration points: Standalone helper type in OM helpers.

Risks: No validation or immutability. Callers must handle null/empty code or message.

Test signals: Basic accessor/mutator coverage if used in response serialization.
