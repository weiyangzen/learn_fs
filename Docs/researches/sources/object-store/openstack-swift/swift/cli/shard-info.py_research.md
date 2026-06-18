# sources/object-store/openstack-swift/swift/cli/shard-info.py

## Purpose
`shard-info.py` is an operator diagnostic script that scans local container databases and prints sharding topology details grouped by root container and shard containers. It reports DB locations, node placement, database state, object/byte counts, sharding sysmeta, own shard ranges, and referenced shard ranges.

## Important APIs, types, and functions
- `broker_key(broker)` loads broker info and uses `broker.path` as the container identity key.
- `container_type(broker)` classifies brokers as `ROOT` or `SHARD`.
- `collect_brokers(conf_path, names2nodes)` reads a container-replicator config, loads the container ring, scans local container DB datadirs, builds `ContainerBroker` instances, and indexes them by container name and node id/index.
- `print_broker_info()`, `print_db()`, `print_own_shard_range()`, `print_shard_range()`, and related helpers produce formatted diagnostic output.
- `print_container()` recursively prints a root or shard container and follows shard range names, avoiding cycles through `used_names`.
- `run(conf_paths)` collects brokers from multiple configs and prints root containers with their shards.

## Control flow
When executed directly, the script lists `/etc/swift/container-server` entries ending in `conf` or `conf.d` and passes those paths to `run()`. Each config is read from its `container-replicator` section to find devices and `swift_dir`. For each container-ring device with a local datadir, `roundrobin_datadirs()` yields DB files. The script creates a `ContainerBroker`, maps the on-disk partition to a primary node index or `handoff`, and stores the broker under its path identity.

Printing starts with root containers detected by any broker reporting `is_root_container()`. For a container, it prints all DB files ordered by node index, flags type mismatches against the expected root/shard type, prints replicated info and raw object count, prints sharding sysmeta, own shard ranges, all shard ranges, and recursively prints each referenced shard container as expected type `SHARD`.

## State and persistence behavior
The script is intended to be read-only. It opens SQLite-backed container brokers and calls broker getters but does not write to DBs. It depends on local device directory state and ring files. The only process state is the recursive `used_names` set that prevents duplicate detail output and cycles.

## Dependencies and integration points
It integrates with container-replicator configuration, the container ring, `roundrobin_datadirs()`, `ContainerBroker`, container sharding metadata, and Swift `Timestamp` formatting. It is useful when debugging container-sharder behavior, misplaced DBs, handoff DBs, or inconsistent shard-range state across replicas.

## Risks and edge cases
There is no argparse or error handling around missing `/etc/swift/container-server`, bad configs, missing rings, corrupt DBs, or absent referenced shard brokers; diagnostics may crash instead of partially reporting. `collect_brokers()` creates a local `brokers` variable that is never populated or used as the return value, so all useful data flows through the passed `names2nodes` defaultdict. The script shadows the built-in name `range` in print helpers. Recursive printing assumes shard range names exist in the collected map; missing local shard DBs can raise a `KeyError`.

## Test signals
Tests should use fake rings, configs, `roundrobin_datadirs()` output, and `ContainerBroker` doubles to cover primary versus handoff node indexing, root/shard type mismatch output, deleted shard range ordering, recursion cycle prevention, missing shard names, multiple config paths, and formatting of delete timestamps and epoch values.
