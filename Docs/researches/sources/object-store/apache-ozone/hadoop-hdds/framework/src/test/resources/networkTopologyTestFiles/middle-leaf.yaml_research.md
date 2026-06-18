# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/middle-leaf.yaml

Purpose: Negative YAML topology fixture where a middle layer is marked as a leaf but still has children.

Important APIs/types/functions: Nested `sublayer` tree with a `rack` node declared `type: LEAF_NODE` while it contains nodegroup and node sublayers.

Control flow: Parser input only; validation should reject a leaf node with children or a leaf in the middle of the hierarchy.

State and persistence behavior: Static YAML resource.

Dependencies and integration points: Used by YAML topology validation tests.

Risks: If parser ignores children under leaf nodes, this fixture could be incorrectly accepted.

Test signals: Negative signal for structural leaf placement validation.
