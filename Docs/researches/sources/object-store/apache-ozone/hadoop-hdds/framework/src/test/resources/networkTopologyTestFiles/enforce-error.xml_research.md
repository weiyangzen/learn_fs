# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/enforce-error.xml

Purpose: XML topology fixture for prefix-enforcement validation failure.

Important APIs/types/functions: Defines `configuration`, `layoutversion`, four `layer` entries, and a `topology` path with `enforceprefix>true</enforceprefix>`.

Control flow: Parser input only. The path `/datacenter/rack/nodegroup/node` references layers where `rack` has prefix `rack` but `nodegroup`/`node` have empty prefixes while enforcement is true.

State and persistence behavior: Static resource file; no runtime state except parser-derived topology model.

Dependencies and integration points: Consumed by network topology parser tests for XML schema and prefix checks.

Risks: Type casing varies (`ROOT`, `InnerNode`, `Leaf`), so parser case-sensitivity is part of the fixture assumptions.

Test signals: Negative signal for enforced prefix validation.
