# sources/object-store/minio/cmd/batch-replicate_test.go

This hand-written test file verifies YAML parsing behavior for batch replication job definitions. The single test, `TestParseBatchJobReplicate`, unmarshals representative YAML into `BatchJobRequest` and checks that the source prefix model accepts both a scalar prefix and a list of prefixes.

The first fixture describes a `replicate` job with API version `v1`, local MinIO source bucket `mytest`, scalar prefix `object-prefix1`, disabled snowball transfer, remote MinIO target endpoint `http://127.0.0.1:9001`, credentials, and filter entries for age, tags, and metadata. After `yaml.Unmarshal`, the test asserts `job.Replicate.Source.Prefix.F()` equals `[]string{"object-prefix1"}`.

The second fixture is structurally similar but changes `source.prefix` to a YAML list containing `object-prefix1` and `object-prefix2`. It asserts the normalized prefix accessor returns both values in order. This is an important integration signal because replication job code consumes normalized prefix slices even though user-facing YAML allows a scalar or list shape.

There is no runtime state or persistence in this test. It depends on `gopkg.in/yaml.v3`, `slices.Equal`, and the batch job request model defined elsewhere. The main risk addressed is accidental breakage of flexible YAML decoding for source prefixes. Uncovered risks include validation of endpoints and credentials, target prefix semantics, snowball option parsing, retry/notify defaults, invalid YAML, remote-source tag restrictions, and execution behavior after parsing.
