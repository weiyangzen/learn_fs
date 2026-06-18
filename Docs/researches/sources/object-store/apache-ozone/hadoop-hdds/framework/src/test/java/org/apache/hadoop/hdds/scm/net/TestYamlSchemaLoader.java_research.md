# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestYamlSchemaLoader.java

## Purpose

This class tests YAML topology schema loading, including invalid root/leaf layouts, a valid fixture, missing files, and the default YAML schema.

## Important APIs, Types, And Functions

It uses `NodeSchemaLoader.getInstance().loadSchemaFromFile`, fixture paths under `networkTopologyTestFiles`, and `NodeSchemaLoader.NodeSchemaLoadResult`.

## Control Flow

Parameterized tests load invalid YAML fixtures and assert expected message substrings. Other tests assert `good.yaml` loads, a missing file throws `FileNotFoundException`, and `network-topology-default.yaml` produces three schema entries.

## State And Persistence

No state persists beyond parsed schema results. Inputs are classpath YAML resources.

## Dependencies And Integration Points

The tests integrate with YAML parsing support in `NodeSchemaLoader` and the default network topology resource shipped with the framework.

## Risks

The tests cover only two invalid YAML layouts and do not duplicate all XML validation cases. Message substring checks are brittle but useful for targeted diagnostics.

## Test Signals

Signals include rejection of multiple-root and middle-leaf schemas, successful good/default YAML loads, missing-file failure, and default schema size of three.
