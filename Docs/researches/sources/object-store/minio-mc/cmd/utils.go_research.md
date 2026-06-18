## sources/object-store/minio-mc/cmd/utils.go

Purpose: shared mc command utilities for error classification, random names, TLS debug output, S3 config construction, truncation, object age filters, bucket lookup mode, URL containment, filesystem metadata parsing, terminal text centering, admin client creation, HTTP client construction, Prometheus JWT generation, and conservative filenames.

Important functions include `isErrIgnored`, `UTCNow`, `randString`, `NewS3Config`, `isOlder`, `isNewer`, `parseAtimeMtime`, `parseAttribute`, `httpClient`, and `getPrometheusToken`. State comes from globals such as `globalDebug`, `globalInsecure`, root CAs, transfer limits, and alias config. Dependencies include minio-go, madmin, JWT, ieproxy, TLS, and `probe`. Risks include fatal parsing in age filters, metadata grammar ambiguity around slash/colon separators, insecure TLS being global, and random string shortening to half the requested length. `utils_test.go` covers attribute parsing only.
