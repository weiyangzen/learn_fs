# sources/distributed-fs/tahoe-lafs/misc/simulators/simulate_load.py

## Purpose

This discrete-event simulator models a Tahoe-like grid with nodes accepting shares, publishing/deleting files, and tracking total utilization over time in an RRD graph.

## Important APIs, Types, and Functions

`sha` and `randomid` generate IDs. `Node` tracks shares, capacity, utilization, and files; key methods are `permute_peers`, `publish_file`, `accept_share`, `make_space`, `delete_share`, `retrieve_file`, and `delete_file`. `Introducer` tracks living files and utilization and coordinates deletion. `Simulator` defines event rates, initializes PyRRD storage, schedules events, handles add/delete file events, records stats, and writes graphs.

## Control Flow

`main` creates a `Simulator`, then processes 1000 scheduled events. Events are exponentially distributed by type; add-file chooses a random node and size, publishes shares through permuted peers, and records success/failure; delete-file asks shuffled nodes to delete one known file. Utilization is buffered into `/tmp/utilization.rrd` and can be graphed to `/tmp/utilization.png`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is `/tmp/utilization.rrd` and optional PNG output. Dependencies are PyRRD/pkg_resources, random, hashlib, and RRD tooling. Risks include Python 2 division, bytes/string hashing, `random.choice(self.shares.keys())` under Python 3, incomplete ADDNODE/DELNODE events, possible `delete` KeyError if metadata drifts, and hard-coded `/tmp` output. Tests should seed randomness, use tiny NUM_NODES/event counts, validate share accounting, deletion accounting, and RRD calls through fakes.
