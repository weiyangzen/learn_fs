<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountv1.go -->
# sources/user-network-fs/blobfuse2/cmd/mountv1.go

Purpose: `mountv1` command that converts legacy Blobfuse v1 config files and CLI flags into Blobfuse2 YAML, then optionally mounts with either the normal v2 mount path or the Gen1 mount path.

Important APIs/types/functions: `blobfuseCliOptions`, `ComponentsConfig`, `PipelineConfig`, many package-global v2 option structs, `resetOptions`, Cobra command `generateConfigCmd`, `parseFuseConfig`, `convertBfConfigParameter`, `convertBfCliParameters`, `yaml.Marshal`, and flags for v1 cache/storage/log/fuse options plus `--convert-config-only`, `--enable-gen1`, and `--required-free-space-mb`.

Control flow: optional version check runs first. The command resets conversion state, records an optional mount path, opens the v1 config file when supplied, scans it line-by-line, strips comments, requires `key value` pairs, and maps supported keys into v2 option structs. CLI flags are then converted and override overlapping file config. `-o` fuse options are parsed separately. The component list starts with `libfuse`, conditionally adds `stream`, `file_cache`, and `attr_cache`, then `azstorage`. If endpoint is not explicitly provided, it builds one from account name, account type, and HTTP/HTTPS settings, falling back to the storage account environment variable. It sets virtual-directory mode, marshals a `PipelineConfig` YAML to `--output-file`, and if not conversion-only invokes either `mountgen1` or `mount` through `rootCmd.Execute`.

State/persistence behavior: writes the converted YAML output file with mode `0700`. When not conversion-only it starts a mount command and may create normal mount/daemon state through `mount.go` or JSON/external process state through `mountgen1.go`. Conversion uses many package-global variables that persist until reset.

Dependencies/integration: integrates legacy config syntax, Cobra/pflag changed-state checks, syslog warnings for unsupported v1 flags, component option structs, Azure storage endpoint rules, environment variable `AZURE_STORAGE_ACCOUNT`, and the main command dispatcher. It shares `ignoreFuseOptions` with mount behavior.

Risks/test signals: scanner-based parsing rejects values split across whitespace and only supports a fixed key set. Some unsupported v1 flags are silently logged and ignored. Streaming cache math can divide by zero if block size/buffer size are not supplied consistently. Endpoint synthesis fails when account name is absent and environment fallback is missing. The broader `mountv1_test.go` suite, though outside this work item, covers config-file and CLI conversions, invalid fuse options, invalid account type/name, unsupported option warnings, and component ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountv1.go -->
