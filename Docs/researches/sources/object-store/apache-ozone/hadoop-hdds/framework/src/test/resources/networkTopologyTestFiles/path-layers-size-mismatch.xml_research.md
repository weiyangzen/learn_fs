# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/path-layers-size-mismatch.xml

Purpose: Negative XML fixture where topology path depth does not match declared layer ordering.

Important APIs/types/functions: Declares layers `datacenter`, `rack`, `node`, but topology path is `/datacenter/node`, omitting `rack`.

Control flow: Parser input only; validation should reject path/layer mismatch.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser path validation tests.

Risks: If parser validates only referenced layer existence, it may miss the omitted middle layer.

Test signals: Negative signal for path-to-layer depth consistency.
