# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/invalid-version.xml

Purpose: Negative XML topology fixture for nonnumeric layout version.

Important APIs/types/functions: `<layoutversion>a</layoutversion>` with otherwise similar layer/topology structure.

Control flow: Parser input only; version parsing should fail before accepting topology.

State and persistence behavior: Static resource.

Dependencies and integration points: Used by topology parser version validation tests.

Risks: The fixture also contains a negative rack cost, so tests expecting a specific error must account for parser validation order.

Test signals: Negative signal for layout version parsing and validation.
