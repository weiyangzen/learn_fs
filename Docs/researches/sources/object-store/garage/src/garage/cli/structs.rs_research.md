# sources/object-store/garage/src/garage/cli/structs.rs

Purpose: This file is the command-line schema for the `garage` binary. It uses `structopt` to define the top-level command tree, subcommands, flags, positional arguments, environment-backed options, version strings, hidden commands, and safety confirmation switches. It is declarative rather than executable; runtime dispatch happens in `main.rs` and the local/remote CLI modules.

Important APIs and types: The central public type is `Command`, with variants for `server`, `health`, `status`, `node`, `layout`, `bucket`, `key`, `admin-token`, `repair`, `offline-repair`, `stats`, `worker`, `block`, `meta`, `convert-db`, `admin-api-schema`, `json-api`, and shell completions. Supporting types include `ServerOpt`, `HealthOpt`, `NodeOperation`, `LayoutOperation`, `BucketOperation`, `KeyOperation`, `AdminTokenOperation`, `RepairOpt`, `RepairWhat`, `ScrubCmd`, `OfflineRepairOpt`, `WorkerOperation`, `WorkerListOpt`, `BlockOperation`, and `MetaOperation`.

Control flow: `structopt` derives generate clap parsing and validation. Nested enums model dispatch boundaries: for example `Command::Bucket(BucketOperation::SetQuotas(...))` and `Command::Repair(RepairOpt { what: RepairWhat::Scrub { cmd } })`. Required arguments, defaults, feature gates, and confirmation flags are enforced at parse time before `main.rs` matches on `Command`.

State and persistence behavior: This file does not persist state. It describes operations that later mutate cluster layout, bucket/key/admin-token metadata, worker parameters, block resync queues, metadata snapshots, and local database conversion. Safety state is represented in the CLI surface through `--yes` flags for destructive operations and by requiring specific version numbers for layout apply/skip operations.

Dependencies and integration points: It depends on `structopt`, clap shell completion support, `bytesize::ByteSize`, `garage_util::version::garage_version`, and the local database conversion option type. It integrates with remote admin RPC handlers, local initialization/repair/conversion code, the admin OpenAPI schema generator, and feature-gated K2V offline repair.

Risks: CLI compatibility is encoded here; renaming flags, changing defaults, or moving variants can break scripts and admin automation. Some high-risk operations are only guarded by flags rather than interactive prompts. Feature-gated variants mean documentation/tests must account for build features. The file is large enough that adding a new command in the wrong enum branch can silently change whether it is handled locally or remotely.

Test signals: Integration tests in this group exercise several CLI paths indirectly: bucket creation/permission changes, key permission changes, layout bootstrap, node ID lookup, website enable/disable, and `json-api CreateKey`. Parse-level coverage is otherwise implicit through successful test harness startup and command invocation.
