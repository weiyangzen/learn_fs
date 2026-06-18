# sources/object-store/minio/cmd/config-dir.go

## Purpose
`config-dir.go` defines default MinIO config and certificate directory locations and the small `ConfigDir` wrapper used by startup and TLS loading.

## Important APIs, Types, And Functions
Constants define `.minio`, `certs`, `CAs`, `public.crt`, and `private.key`. `ConfigDir` wraps a path with `Get`. `getDefaultConfigDir`, `getDefaultCertsDir`, and `getDefaultCertsCADir` derive paths from the user home directory. `defaultConfigDir`, `defaultCertsDir`, `defaultCertsCADir`, `globalConfigDir`, `globalCertsDir`, and `globalCertsCADir` hold defaults/current directories. `mkdirAllIgnorePerm` creates directories while ignoring permission errors. `getConfigFile`, `getPublicCertFile`, and `getPrivateKeyFile` build current file paths.

## Control Flow
Defaults are computed at package initialization. Startup may replace globals through `newConfigDir` and `handleCommonArgs` in `common-main.go`; later helpers read the current paths.

## State And Persistence Behavior
The only filesystem mutation is directory creation with mode `0700`. Ignoring permission errors supports mounted read-only or externally managed paths.

## Dependencies And Integration Points
It depends on `go-homedir`, `os`, and `filepath`. It is used by config migration, TLS certificate loading, Console cert configuration, and KMS CA lookup.

## Risks And Test Signals
If home lookup fails, default paths become empty and startup must reject them unless explicitly set. Ignored permission errors can defer failures to later file reads. No direct tests are in this subset; startup integration covers the behavior.
