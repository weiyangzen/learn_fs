## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/client.py

Purpose: thin test client that runs Ozone shell and Freon commands inside the cluster's `ozone_client` docker container.

Important APIs/types/functions: `OzoneClient` stores an `OzoneCluster`. `create_volume` runs `ozone sh volume create`. `create_bucket` runs `ozone sh bucket create`. `put_key` validates the source file inside the client container and runs `ozone sh key put`, optionally with `--replication`. `get_key` runs `ozone sh key get`. `run_freon` builds an `ozone freon rk` command with volume, bucket, key count, key size, replication type, and replication factor.

Control flow: callers obtain it through `OzoneCluster.get_client()`, prepare volumes/buckets/keys or use `run_freon` to generate data, then assert exit status. `run_freon` intentionally returns `(exit_code, output)` for tests to assert later.

State and persistence behavior: creates Ozone volumes, buckets, keys, and downloaded files in the client container. It does not cache Ozone metadata locally.

Dependencies and integration points: imports `ozone.util.run_docker_command` and `Command` from `ozone.cluster`/constants. Used throughout blockade tests to seed containers and verify client-visible recovery.

Risks: command arguments are concatenated into shell strings; API assumes root user and fixed Ozone CLI shape; replication option spelling must match the Freon/key command versions. Importing `Command` through `ozone.cluster` relies on a re-export side effect.

Test signals: tested by end-to-end blockade tests where Freon and key put/get must succeed across partition restore.
