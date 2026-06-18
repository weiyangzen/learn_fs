# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-topology.xml

Purpose: Negative XML fixture with duplicate `topology` sections.

Important APIs/types/functions: Contains one `layers` section and two identical `topology` elements.

Control flow: Parser input only; validation should reject ambiguous multiple topology definitions.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser validation tests.

Risks: If parser accepts the first or last topology silently, configuration ambiguity would go undetected.

Test signals: Negative signal for exactly one topology block requirement.
