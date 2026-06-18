# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/config_test.go

Purpose: unit tests for config parsing.

Important flow: table-driven cases write temporary config content with `declare` and simple `KEY=value` forms, call `Get`, and compare parsed `kv` maps with expected maps. Tests assert malformed spacing is ignored and empty values can be represented.

State and dependencies: uses `/tmp/gce-xfstests-test.config`; depends on reflection equality and local filesystem writes.

Integration points: protects the parser used by server auth/config, GCP project lookup, bucket selection, and internal IP discovery.

Risks and test signals: tests focus on parser shape, not concurrent `Update`, global init paths, or values containing spaces. They are hermetic aside from the package init requiring the real appliance config unless adjusted by the test environment.
