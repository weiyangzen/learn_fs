# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-root.xml

Purpose: Negative XML fixture with multiple root layers.

Important APIs/types/functions: Both `datacenter` and `rack` layers are declared `ROOT`.

Control flow: Parser input only; validation should reject more than one root in the topology hierarchy.

State and persistence behavior: Static resource.

Dependencies and integration points: Network topology XML validation tests.

Risks: Type casing and default path syntax must align with parser expectations to isolate the root-count failure.

Test signals: Negative signal for single-root topology invariant.
