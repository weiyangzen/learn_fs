# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/good.yaml

Purpose: Valid YAML network topology fixture.

Important APIs/types/functions: Root object with `cost`, `prefix`, `type`, `defaultName`, and nested `sublayer` arrays down to a leaf node.

Control flow: Parser input only; expected to produce root -> datacenter -> rack -> nodegroup -> node.

State and persistence behavior: Static YAML resource.

Dependencies and integration points: Positive fixture for YAML topology parser tests.

Risks: YAML comments document schema expectations such as explicit prefixes for inner nodes; parser/schema changes may require coordinated fixture updates.

Test signals: Baseline positive signal for YAML topology parsing.
