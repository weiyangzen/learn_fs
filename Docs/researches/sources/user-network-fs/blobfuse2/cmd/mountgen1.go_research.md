<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountgen1.go -->
# sources/user-network-fs/blobfuse2/cmd/mountgen1.go

Purpose: hidden `mountgen1` command that converts Blobfuse2-style config into an `adlsgen1fuse` JSON file and optionally runs the external ADLS Gen1 fuse binary.

Important APIs/types/functions: globals `azStorageOpt`, `libFuseOpt`, `fileCacheOpt`, `requiredFreeSpace`, `configFile`, `generateJsonOnly`, `gen1ConfigFilePath`; `resetGenOneOptions`; Cobra command `gen1Cmd`; `generateAdlsGenOneJson`; `runAdlsGenOneBinary`; `azstorage.AzStorageOptions`; `libfuse.LibfuseOptions`; and `file_cache.FileCacheOptions`.

Control flow: reset Gen1-specific options, parse the supplied config, unmarshal mount/logging options, validate the mount path, unmarshal `azstorage`, require account name, tenant ID, and client ID, default auth mode to `spn` when empty, unmarshal `libfuse` and `file_cache`, parse log level, generate the JSON config, and run `adlsgen1fuse <json>` unless `--generate-json-only` is true. JSON generation maps SPN auth to servicePrincipal credentials, sets authority/resource URLs, copies fuse timeout and allow-other settings, logging, retry/cache/free-space options, cache path, resource ID, and mount directory.

State/persistence behavior: writes the JSON file at `--output-file` or `/tmp/adlsgen1fuse.json` with mode `0777`. It intentionally omits the client secret because `adlsgen1fuse` reads `ADL_CLIENT_SECRET` from the environment. Running without generate-only starts an external mount process.

Dependencies/integration: depends on `parseConfig`, mount option validation, config unmarshalling for azstorage/libfuse/file_cache, and the `adlsgen1fuse` binary. It is also used by `mountv1 --enable-gen1` after converting v1 config.

Risks/test signals: only SPN auth is supported; other auth modes fail. The JSON file permission is broad. External binary absence is an expected failure in tests. Tests verify JSON creation, required config validation, invalid auth mode, and external-run failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountgen1.go -->
