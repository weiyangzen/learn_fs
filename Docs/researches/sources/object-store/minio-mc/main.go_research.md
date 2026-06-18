## sources/object-store/minio-mc/main.go

Purpose: minimal process entry point for the mc command binary. It imports `github.com/minio/mc/cmd` as `mc`, calls `mc.Main(os.Args)`, and terminates through `console.Fatalln` if an error is returned.

Control flow is a single delegation from package `main`; all CLI registration, globals, and command behavior live in `cmd`. State is limited to process arguments and exit behavior. Dependencies are `os`, the mc command package, and MinIO console output. Integration is the build target import path `github.com/minio/mc`. Risks are low; the main concern is that any returned error is fatal and formatting is controlled by console. Test signal is normally covered by command package tests or binary smoke tests, not this file directly.
