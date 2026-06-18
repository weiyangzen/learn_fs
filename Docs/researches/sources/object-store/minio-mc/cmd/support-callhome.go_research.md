<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-callhome.go -->
# sources/object-store/minio-mc/cmd/support-callhome.go

Purpose: implements `mc support callhome enable|disable|status ALIAS`, a support subcommand that manages MinIO server callhome configuration.

Important APIs/types/functions: `supportCallhomeCmd` defines the CLI; `supportCallhomeMessage` renders text and JSON output; `isDiagCallhomeEnabled`, `mainCallhome`, `printCallhomeStatus`, `toggleCallhome`, and `setCallhomeConfig` implement status and mutation.

Control flow: `mainCallhome` initializes license/support colors, validates the two-argument toggle syntax through shared support helpers, and requires cluster registration for non-development operation. `status` reads the server config via `isFeatureEnabled`; `enable` and `disable` call `setCallhomeConfig`, which creates an admin client, checks subsystem support, and writes `callhome enable=on|off`.

State and persistence: persistent state is stored in the remote MinIO server config through `madmin.AdminClient.SetConfigKV`. The command itself only emits output.

Dependencies and integration points: depends on shared support registration checks, MinIO admin config APIs, `madmin.Default`, `minioConfigSupportsSubSys`, and global JSON/text output plumbing.

Risks and test signals: risks include server-version compatibility and permission/configuration failures. Useful tests should cover invalid toggle args, unsupported subsystem handling, JSON output, and status behavior when the `enable` key is absent or explicitly off.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-callhome.go -->
