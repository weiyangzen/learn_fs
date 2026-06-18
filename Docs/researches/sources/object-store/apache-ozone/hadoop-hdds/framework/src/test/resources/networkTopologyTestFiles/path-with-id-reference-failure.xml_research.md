# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/path-with-id-reference-failure.xml

Purpose: Negative XML fixture where topology path references an undeclared layer id.

Important APIs/types/functions: Declares `datacenter`, `rack`, `node`; topology path uses `/datacenter/room/node`.

Control flow: Parser input only; validation should fail resolving `room`.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser ID reference validation tests.

Risks: Error reporting should identify the missing path segment rather than a generic path mismatch.

Test signals: Negative signal for path layer ID reference validation.
