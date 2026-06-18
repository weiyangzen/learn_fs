## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/exceptions.py

Purpose: custom exception for missing Ozone containers in blockade tests.

Important APIs/types/functions: `ContainerNotFoundError(RuntimeError)` formats a message as `Container not found. ID = <id>` and passes it to `RuntimeError`.

Control flow: raised by `OzoneCluster.get_container` and `get_container_state` when SCM/datanode metadata lookups fail. `Container` wait predicates catch it where absence is acceptable while polling.

State and persistence behavior: no persistent state beyond the exception message.

Dependencies and integration points: imported by `ozone.cluster`, `ozone.container`, and `test_blockade_datanode_isolation.py`.

Risks: the constructor ignores extra positional/keyword args besides the first container ID, so callers should only pass the ID. The message is simple but sufficient for test diagnostics.

Test signals: missing container paths in blockade tests surface through this exception or through wait predicate retries.
