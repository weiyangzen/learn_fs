# sources/object-store/minio-mc/cmd/config-utils_test.go

Purpose: Unit tests for basic config utility validators.

Important APIs/types/functions: `TestValidHostURL`, `TestIsValidAPI`, `TestValidSecretKeys`, `TestValidAccessKeys`, and helper `equalAssert`.

Control flow: Tests use small table-style inputs and fail on mismatches. They verify that `https://localhost:9000` is a host URL, `/` is not, mixed-case S3 API values are accepted, and key length minimums are enforced while empty keys are accepted.

State and persistence: No state or filesystem use.

Dependencies/integration: Uses Go `testing`; exercises functions from `config-utils.go`.

Risks: Coverage is narrow. It does not test `isValidLookup`, `isValidPath`, trailing separator trimming, malformed schemes, or URL path rejection.

Test signals: Positive signal for intended anonymous-key behavior and minimum-length boundaries.
