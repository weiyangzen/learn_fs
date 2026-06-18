# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_multi_introducers.py

## Purpose
Tests client configuration for multiple introducers, deprecated `[client] introducer.furl`, `private/introducers.yaml`, default conflict rejection, invalid historical YAML, and introducerless clients.

## APIs / Types / Functions
- `MultiIntroTests` and `NoDefault` create node basedirs with storage disabled.
- `write_node_config` writes baseline node config.
- `create_client` is the integration point under test.
- YAML fixtures include valid simple YAML and invalid `one: furl = furl1` form.

## Control Flow
Tests write YAML with two introducers and count `myclient.introducer_clients`; read deprecated tahoe.cfg FURL and verify a deprecation warning; reject simultaneous tahoe.cfg FURL and YAML `default`; accept named YAML introducers; reject invalid equals-style YAML; and allow an empty introducer map.

## State And Persistence
Writes `tahoe.cfg`, `private/introducers.yaml`, and private directories in temporary basedirs. Resulting client state includes constructed introducer clients.

## Dependencies / Integration Points
Integrates config writer, YAML parser/serializer, client creation, deprecation warning handling, and introducer-client setup.

## Risks And Test Signals
Some constants are unused, showing historical drift. Exact warnings/errors are asserted. Passing tests show multi-introducer config and migration from deprecated config remain safe and explicit.
