# sources/object-store/garage/src/garage/tests/common/client.rs

Purpose: This helper builds the AWS S3 SDK client used by Garage integration tests.

Important APIs and types: `build_client` takes a test `garage::Key` and returns `aws_sdk_s3::Client`. It constructs `Credentials`, `Config::builder`, endpoint URL using `DEFAULT_PORT`, shared test region, and `BehaviorVersion::latest`.

Control flow: The function creates static credentials from the generated test key, sets endpoint `http://127.0.0.1:{DEFAULT_PORT}`, assigns `garage-integ-test` region, sets credentials provider, chooses the latest SDK behavior version, builds config, and returns a client from that config.

State and persistence behavior: There is no persistence. The function captures connection/authentication state in an SDK client object that later signs S3 requests against the test daemon.

Dependencies and integration points: It depends on `aws_sdk_s3`, shared `REGION`, `garage::Key`, and `DEFAULT_PORT`. It is used by `Context::new` so almost every S3 integration test goes through it.

Risks: The endpoint is tied to `DEFAULT_PORT` rather than the instance's selected port, while `garage::Instance` can read `GARAGE_TEST_INTEGRATION_PORT`. If tests run with a non-default port, this helper can become inconsistent with the server instance unless the default remains aligned.

Test signals: All AWS SDK integration tests implicitly validate that credentials, region, endpoint, and behavior version interoperate with Garage's S3 API.
