# sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/ReplicateAnnotationProcessor.java

Purpose: Validates methods annotated with `org.apache.hadoop.hdds.scm.metadata.Replicate`. The processor enforces that replicated SCM metadata operations declare the expected checked exception contract.

Important APIs/types/functions: `ANNOTATION_NAME` identifies the processed annotation. `REQUIRED_EXCEPTION` is `org.apache.hadoop.hdds.scm.exceptions.SCMException`. `init` resolves the required exception type. `checkMethodSignature` verifies the annotated element is an executable method and that one of its declared thrown types is assignable from the required exception type.

Control flow: During each processing round, `process` finds the matching annotation by qualified name and checks every annotated element. Non-method elements receive an error. Methods without `SCMException` or a parent exception in `throws` receive an error attached to the method.

State and persistence behavior: The processor caches `requiredException` for the processing environment. It has no runtime persistence.

Dependencies and integration points: Depends on javac processing APIs and the SCM exception class being available on the annotation-processing classpath. It supports the metadata replication layer by keeping generated/proxied replicated methods compatible with failure semantics.

Risks: If the required exception type cannot be resolved, `init` can fail before a useful compiler diagnostic. The assignability direction accepts declared parent exceptions, matching the message, but should be checked if subclasses of `SCMException` are intended to be accepted.

Test signals: Compile tests should verify methods throwing `SCMException`, methods throwing `Exception`, methods throwing no exception, methods throwing unrelated exceptions, and accidental annotation on non-method elements.
