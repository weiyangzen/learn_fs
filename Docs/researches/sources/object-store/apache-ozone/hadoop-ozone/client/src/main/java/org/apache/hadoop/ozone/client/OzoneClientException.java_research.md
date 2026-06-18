## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientException.java

### Purpose
`OzoneClientException` is a client-specific checked exception that extends `IOException`. It provides constructors matching the common Java exception shapes.

### Important APIs and Types
Constructors support no-arg, message-only, message-plus-cause, and cause-only initialization. No extra fields or behavior are added.

### Control Flow
There is no operational control flow beyond superclass constructor calls.

### State and Persistence Behavior
The exception stores standard `Throwable` state only. It has no persistence effects.

### Dependencies and Integration Points
It integrates with Java I/O exception handling and can be used by Ozone client APIs without forcing a non-IO checked exception hierarchy.

### Risks and Edge Cases
The class has no `serialVersionUID`, which can trigger serialization warnings but is common for simple exceptions. Because it adds no structured result code, callers needing OM-specific causes must inspect wrapped exceptions.

### Test Signals
Constructor tests can verify message and cause propagation, although coverage value is low unless serialization or public API compatibility is under review.
