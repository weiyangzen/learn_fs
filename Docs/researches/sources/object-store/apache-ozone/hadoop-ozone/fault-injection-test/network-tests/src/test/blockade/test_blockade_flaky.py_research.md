## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_flaky.py

Purpose: pytest scenario for blockade's `flaky` mode applied to datanode containers while Ozone continues handling Freon load.

Important APIs/types/functions: `test_flaky(flaky_node)` is parameterized with `"datanode"`. Setup/teardown starts and stops `OzoneCluster`. It imports `Blockade` directly.

Control flow: chooses one datanode at random from `cluster.datanodes`, calls `Blockade.make_flaky`, runs Freon workload, then calls `Blockade.blockade_fast_all` to restore normal network speed/loss behavior.

State and persistence behavior: mutates blockade network impairment state and creates Ozone data through Freon. Does not inspect container metadata.

Dependencies and integration points: depends on `pytest`, `random`, `OzoneCluster`, and `Blockade`.

Risks: random node selection makes failures less reproducible unless test logs record the selected node; only datanode is parameterized despite a generic argument name; no `finally` around `blockade_fast_all` inside the test body.

Test signals: Freon exit code under a flaky datanode and ability to clear impairment with `fast --all`.
