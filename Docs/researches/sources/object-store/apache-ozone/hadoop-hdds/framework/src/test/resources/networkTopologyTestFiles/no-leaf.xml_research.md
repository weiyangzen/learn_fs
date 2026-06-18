# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-leaf.xml

Purpose: Negative XML fixture with no leaf layer.

Important APIs/types/functions: All path layers are root or inner nodes; terminal `node` is `InnerNode`.

Control flow: Parser input only; validation should require a terminal leaf.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology validation tests.

Risks: If parser infers terminal path elements as leaves regardless of explicit type, this fixture may be accepted incorrectly.

Test signals: Negative signal for required leaf layer.
