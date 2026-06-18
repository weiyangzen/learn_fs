<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_all.go -->
# sources/user-network-fs/blobfuse2/cmd/mount_all.go

Purpose: `mount all [path]` subcommand that enumerates all containers in an Azure Storage account and starts a separate Blobfuse2 mount for each allowed container.

Important APIs/types/functions: `containerListingOptions`, global `mountAllOpts`, Cobra command `mountAllCmd`, `processCommand`, `getContainerList`, `filterAllowedContainerList`, `mountAllContainers`, `updateCliParams`, `writeConfigFile`, `buildCliParamForMount`, `ignoreCliParam`, `azstorage.AzStorage`, `viper`, and `yaml`.

Control flow: `processCommand` reads the default or supplied config, unmarshals mount options, validates the base mount path while allowing non-empty directories, initializes logging, sets `mount-path` and `mount-all-containers`, unmarshals `mountall` allow/deny lists, validates secure-config passphrase if needed, lists containers through an `azstorage` component, filters the list, and mounts each remaining container. `mountAllContainers` derives per-container mount paths and config filenames, creates mount directories, sets container-specific config keys, writes plain or encrypted per-container config files when an input config exists, or injects container/tmp-path CLI flags when running from environment/defaults, then invokes the current blobfuse2 binary with `mount` arguments and disables version checks.

State/persistence behavior: creates one subdirectory per mounted container under the requested path, writes per-container config files under `common.DefaultWorkDir`, mutates viper state between containers, and starts daemonized child mounts. It accumulates failure count but returns nil after per-container failures unless config writing or setup fails.

Dependencies/integration: depends on Azure storage credentials/config sufficient for `azstorage.Configure`, `Start`, and `ListContainers`; reuses `parseConfig`, `options.validate`, log setup, secure config crypto, and the main `mount` command via subprocess. Allow/deny lists come from the `mountall` config section.

Risks/test signals: map iteration in `filterAllowedContainerList` returns containers in nondeterministic order. Reusing mutable global viper state across containers can leak settings if not reset carefully. Shelling out to `os.Args[0]` assumes the current binary path is executable. Tests in `mount_test.go` cover validation failures and `updateCliParams`; full multi-container behavior depends on live Azure integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_all.go -->
