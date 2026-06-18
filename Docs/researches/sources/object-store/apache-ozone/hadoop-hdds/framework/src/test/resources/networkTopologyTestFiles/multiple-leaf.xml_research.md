# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-leaf.xml

Purpose: Negative XML fixture with multiple leaf layers in one path.

Important APIs/types/functions: Both `rack` and `node` layers are declared `Leaf`.

Control flow: Parser input only; validation should reject a hierarchy where an intermediate layer is a leaf.

State and persistence behavior: Static resource.

Dependencies and integration points: Network topology XML validation tests.

Risks: The fixture relies on topology path ordering to expose the intermediate leaf error.

Test signals: Negative signal for exactly one terminal leaf requirement.
