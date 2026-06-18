# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/resources/network-topology-default.xml

## Purpose
This XML resource defines the default HDDS/Ozone network topology schema. It models a three-level topology: root datacenter, rack, and leaf node.

## Important APIs, Types, And Functions
The root element is `<configuration>`. `<layoutversion>1</layoutversion>` declares the schema version. `<layers>` defines three layers: `datacenter` with empty prefix, cost `1`, and type `Root`; `rack` with prefix `rack`, cost `1`, type `InnerNode`, and default `/default-rack`; and `node` with empty prefix, cost `0`, and type `Leaf`. `<topology>` defines the ordered path `/datacenter/rack/node` and sets `<enforceprefix>false</enforceprefix>`.

## Control Flow
At runtime this file is loaded by network topology schema/parsing code when the configured topology file is `network-topology-default.xml`. The loader reads layer definitions, validates the topology path against layer ids, applies defaults for missing rack segments, and uses cost/type information when constructing topology nodes.

## State And Persistence
The file is static classpath configuration. It does not change at runtime, but its parsed representation drives in-memory network topology state for node placement and distance/cost decisions.

## Dependencies And Integration Points
The default name is referenced by HDDS configuration (`ozone-default.xml`) and `ScmConfigKeys`. It integrates with SCM node/network topology code and tests that exercise default and nodegroup topology resources.

## Risks
Because `enforceprefix` is false and root/node prefixes are empty, invalid or inconsistent location strings may pass prefix validation. Changing layer ids, path order, costs, or defaults can affect rack awareness and placement behavior cluster-wide. XML and YAML defaults use different schema shapes, so parity assumptions need explicit tests.

## Test Signals
Tests should load the resource from the classpath, validate layout version, parse all layer types, accept paths with missing rack via `/default-rack`, reject invalid layer references, and verify node distance/cost behavior. SCM node manager topology tests and schema loader tests are relevant integration signals.
