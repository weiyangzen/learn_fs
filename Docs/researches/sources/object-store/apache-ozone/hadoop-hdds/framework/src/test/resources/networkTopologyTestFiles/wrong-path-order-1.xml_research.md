# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/wrong-path-order-1.xml

Purpose: Negative XML fixture with topology path order starting at the wrong layer.

Important APIs/types/functions: Declared layers are root `datacenter`, inner `rack`, leaf `node`, but topology path is `/rack/datacenter/node`.

Control flow: Parser input only; validation should reject layer order inconsistent with declared hierarchy.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology path-order validation tests.

Risks: If parser builds hierarchy solely from the path order, it may miss type-order violations.

Test signals: Negative signal for root-first path ordering.
