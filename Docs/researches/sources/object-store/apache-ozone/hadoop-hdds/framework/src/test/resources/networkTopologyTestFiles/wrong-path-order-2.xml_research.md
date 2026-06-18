# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/wrong-path-order-2.xml

Purpose: Negative XML fixture with leaf and inner layer order swapped.

Important APIs/types/functions: Declared layers are `datacenter` root, `rack` inner, `node` leaf, but topology path is `/datacenter/node/rack`.

Control flow: Parser input only; validation should reject a leaf before an inner layer.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology path-order validation tests.

Risks: Parser must validate both ID existence and semantic ordering to catch this.

Test signals: Negative signal for terminal leaf ordering.
