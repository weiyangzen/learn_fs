# sources/object-store/minio/cmd/testdata/config/invalid-disks.yaml

Purpose: negative YAML fixture for endpoint/disk-count validation. It mostly mirrors a valid two-pool HTTPS config, but one endpoint uses a single disk path (`/mnt/disk1/`) where peer endpoints use `disk{1...4}`.

Important structure: `version`, addresses, certs dir, options, and pool count are otherwise valid. The intentional defect is the first endpoint in the first pool: `https://server-example-pool1:9000/mnt/disk1/`.

Control flow and integration: config parser tests should load the YAML syntactically, expand endpoint patterns, then reject the topology because disk counts are inconsistent within the erasure pool.

State and persistence: static negative fixture only. It should not produce a usable persisted server config.

Dependencies: relies on MinIO's endpoint expansion and erasure topology validation rules.

Risks: if validation becomes too permissive, this fixture would no longer fail and could allow uneven drive topology into distributed setup. If validation rules intentionally change, this fixture must be updated with the expected error behavior.

Test signals: expected result is a validation failure tied to inconsistent disk/cardinality configuration, not a YAML syntax failure.
