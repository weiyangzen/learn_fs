# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/unknown-layer-type.xml

Purpose: Negative XML fixture with an unsupported layer type.

Important APIs/types/functions: Terminal `node` layer has `<type>leaves</type>` rather than a supported root/inner/leaf value.

Control flow: Parser input only; validation should reject unknown type values.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser type validation tests.

Risks: Parser should not normalize arbitrary plural or typo values into leaf.

Test signals: Negative signal for strict layer type parsing.
