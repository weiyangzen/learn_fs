## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKeyLocation.java

### Purpose
`OzoneKeyLocation` is a small immutable DTO describing one block location for a key: container ID, local block ID, length, block offset, and key offset.

### Important APIs and Types
The constructor sets `containerID`, `localID`, `length`, `offset`, and `keyOffset`. Getters expose each value.

### Control Flow
There is no behavior beyond construction and getters.

### State and Persistence Behavior
The object is immutable and local-only. It reflects OM block-location metadata at the time a key detail response was built.

### Dependencies and Integration Points
It is used by `OzoneKeyDetails` to expose data placement information to clients and diagnostic tools.

### Risks and Edge Cases
No validation prevents negative or inconsistent offsets/lengths; correctness depends on conversion code that builds the DTO from OM metadata.

### Test Signals
Tests are simple constructor/getter checks or conversion tests from OM location info in the code that creates `OzoneKeyDetails`.
