# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-root.xml

Purpose: Negative XML fixture with no root layer.

Important APIs/types/functions: Top path layer `datacenter` is declared `InnerNode` instead of `Root`.

Control flow: Parser input only; validation should reject topology without a root.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology validation tests.

Risks: If parser assumes the first layer is root regardless of type, this fixture can catch that bug.

Test signals: Negative signal for explicit root requirement.
