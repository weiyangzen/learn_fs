# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-root.yaml

Purpose: Negative YAML fixture with a root nested under another root.

Important APIs/types/functions: Top-level node has `type: ROOT`; its first child also has `type: ROOT`.

Control flow: Parser input only; validation should reject multiple root nodes.

State and persistence behavior: Static YAML resource.

Dependencies and integration points: YAML topology parser validation tests.

Risks: If validation only checks the top-level node, nested root misuse may be missed.

Test signals: Negative signal for root uniqueness in YAML topology.
