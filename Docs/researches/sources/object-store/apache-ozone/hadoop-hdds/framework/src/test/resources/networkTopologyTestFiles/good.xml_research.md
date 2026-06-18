# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/good.xml

Purpose: Valid XML network topology fixture.

Important APIs/types/functions: Defines layout version 1, layers for datacenter/root, rack, nodegroup, and node/leaf, default locations for inner layers, and topology path `/datacenter/rack/nodegroup/node` with prefix enforcement enabled.

Control flow: Parser input only; expected to build a valid ordered topology hierarchy.

State and persistence behavior: Static resource file.

Dependencies and integration points: Positive fixture for network topology XML parsing and validation tests.

Risks: Prefixes and defaults encode expected parser conventions; changing network topology schema requires updating this fixture.

Test signals: Baseline positive signal for XML topology parsing.
