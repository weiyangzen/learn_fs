## sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/InsufficientLocationsException.java

**Purpose:** Defines the checked exception used by erasure-coded input streams when the client cannot assemble enough readable EC locations to satisfy a read. It is intentionally narrow and extends `IOException`, allowing callers in the Ozone read path to handle it through normal stream error contracts.

**Important APIs/types/functions:** `InsufficientLocationsException` provides the standard four `IOException` constructor shapes: no-arg, message, message-plus-cause, and cause. There is no custom state, serialization field, or behavior.

**Control flow:** The class has no internal branching. Runtime control flow is entirely at throw sites in EC read/reconstruction code, where this type differentiates location quorum failures from checksum, security, EOF, or generic I/O failures.

**State and persistence:** Stateless except for inherited throwable message/cause/stack trace. It is not persisted directly, but may cross API boundaries as part of client read failure reporting.

**Dependencies and integration points:** Depends only on `java.io.IOException`. It is integrated by EC read classes such as reconstructed stripe streams and by tests that assert insufficient EC locations fail deterministically.

**Risks:** Because the type carries no structured metadata, callers cannot inspect missing indexes or failed datanodes unless the thrower encodes details in the message or uses a different exception. Changes to its inheritance would be source and behavior incompatible with stream APIs.

**Test signals:** The listed EC reconstructed-stripe tests assert this exception when too many locations fail, when available blocks are shorter than required, and when all usable locations fail on first read.
