# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-topology.xml

Purpose: Negative XML fixture missing the `topology` section.

Important APIs/types/functions: Defines valid-looking `layers` but no `topology` path/enforcement block.

Control flow: Parser input only; validation should reject incomplete configuration.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser validation tests.

Risks: Parser defaults could mask the missing topology if not explicitly checked.

Test signals: Negative signal for required topology block.
