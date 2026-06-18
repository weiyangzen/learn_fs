# sources/object-store/rustfs/crates/e2e_test/src/reliant/lifecycle.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/lifecycle.rs

Purpose: live-server tests for S3 bucket lifecycle configuration acceptance and expiration behavior.

Important APIs and functions: `create_aws_s3_client` builds the localhost AWS SDK S3 client. `setup_test_bucket` creates `test-basic-bucket` and tolerates existing-bucket strings. `test_bucket_lifecycle_configuration` uses `BucketLifecycleConfiguration`, `LifecycleRule`, `LifecycleRuleFilter`, and `LifecycleExpiration`. `test_bucket_lifecycle_accepts_zero_days` verifies lifecycle rules with `days(0)` are accepted.

Control flow: the expiration test uploads a target object and an untouched object, confirms both exist, creates an enabled lifecycle rule with a prefix matching only the target key and an expiration date set to yesterday midnight UTC, stores the config, verifies the rule can be read back, then polls up to 150 seconds for the target object to become `NoSuchKey`. It finally asserts the nonmatching key still exists. The zero-days test writes a rule with prefix `zero-days/` and expiration `days=0`, expecting the server to accept the configuration without immediate object assertions.

State and persistence: lifecycle rules persist on `test-basic-bucket`, objects persist until lifecycle scanner deletes them or manual cleanup occurs. The first test relies on RustFS background scanner timing and comments that default scanner interval is 60 seconds plus jitter.

Dependencies and integration points: AWS SDK lifecycle types, chrono UTC date handling, Tokio time polling, RustFS lifecycle scanner, bucket metadata persistence, and `serial_test`.

Risks: ignored by default and needs live server plus background lifecycle processing. Fixed bucket and keys can interact with prior lifecycle config. Polling for 150 seconds is expensive and still timing-sensitive. String-based existing-bucket error detection is less precise than service-error code checks.

Test signals: confirms lifecycle config round trip, immediate expiration via past date, prefix scoping, and acceptance of zero-day expiration rules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/lifecycle.rs -->
