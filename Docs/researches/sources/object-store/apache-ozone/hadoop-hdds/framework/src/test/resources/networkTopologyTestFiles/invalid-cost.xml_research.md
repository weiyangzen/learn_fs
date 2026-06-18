# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/invalid-cost.xml

Purpose: Negative XML topology fixture for invalid layer cost.

Important APIs/types/functions: Layer `rack` has `<cost>-1</cost>` while costs are expected to be nonnegative.

Control flow: Parser input only; validation should reject the configuration.

State and persistence behavior: Static resource.

Dependencies and integration points: Used by topology parser validation tests.

Risks: Also includes mixed type casing and defaults; tests should ensure the intended failure is cost, not another validation branch.

Test signals: Negative signal for cost validation.
