<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support.go -->
# sources/object-store/minio-mc/cmd/support.go

Purpose: defines the top-level `mc support` command, shared support flags/helpers, registration enforcement, feature-status helpers, and JSON utility.

Important APIs/types/functions: `supportGlobalFlags`, `supportSubcommands`, `supportCmd`, `toggleCmdArgs`, `validateToggleCmdArg`, `checkToggleCmdSyntax`, `setSuccessMessageColor`, `setErrorMessageColor`, `featureStatusStr`, `validateClusterRegistered`, `isFeatureEnabled`, `toJSON`, and `mainSupport`.

Control flow: `supportCmd` wires subcommands for register/callhome/diag/perf/inspect/profile/top/proxy/upload. Toggle helpers enforce `enable|disable|status ALIAS`. `validateClusterRegistered` checks whether SUBNET registration is required based on dev and airgap modes, then retrieves the SUBNET API key. `isFeatureEnabled` reads server config, handles unsupported subsystems and missing targets, and treats absent `enable` keys as enabled.

State and persistence: this file does not mutate state directly except color registry changes; it reads remote config and SUBNET registration info.

Dependencies and integration points: central integration point for support subcommands, MinIO admin client/config helpers, `madmin` config constants, console color tags, and global CLI flags.

Risks and test signals: registration logic is subtle: commands that talk to SUBNET require stricter dev+airgap bypass behavior. Tests should cover registration combinations, missing config targets, default target mapping, unsupported subsystems, and JSON marshal failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support.go -->
