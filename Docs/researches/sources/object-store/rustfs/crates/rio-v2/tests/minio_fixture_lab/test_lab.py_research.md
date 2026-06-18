# sources/object-store/rustfs/crates/rio-v2/tests/minio_fixture_lab/test_lab.py

Purpose: this unittest suite validates deterministic, server-independent behavior of the MinIO fixture lab CLI. It intentionally avoids launching MinIO and instead tests selection, request construction, XML generation, and KMS configuration helpers.

Important tests and control flow: `load_lab_module` imports sibling `lab.py` dynamically so tests can run without package installation. `DiscoverMinioLauncherTests` verifies explicit binary preference, bundled default use via monkeypatched `DEFAULT_MINIO_BINARY`, rejection of a source checkout without a binary when `PATH` lookup is mocked missing, and `minio.exe` discovery under `--minio-root`. `FixtureMatrixTests` asserts the default matrix has six cases and covers SSE-S3/SSE-KMS/SSE-C across singlepart 64 KiB and multipart 8 MiB shapes, plus configured KMS key IDs. `RequestRecordTests` checks KMS context base64 formatting, SSE-S3 AES256 headers, and SSE-C customer key headers. `MultipartManifestTests` checks completion XML. `KmsSecretKeyTests` checks key-id parsing, rejection of missing separators, and env payload generation.

State and persistence: tests create temporary directories and monkeypatch module globals, restoring the bundled binary setting in `finally` blocks. No repo artifacts or fixture cases are written.

Dependencies and integration points: depends only on Python standard library. It gives fast feedback for the lab script that produces artifacts consumed by Rust ignored fixture tests.

Risks and test signals: the suite does not validate live MinIO startup, SigV4 request signing against a real server, backend artifact copying under real object layouts, TLS certificate generation, or cleanup behavior. It is strongest at preventing accidental changes to fixture IDs, header shapes, and launcher precedence, which are the stable contracts used by downstream fixture consumers.
