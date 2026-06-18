<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/permission_option.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/permission_option.rs

Purpose: defines user-facing FUSE permission options.

Important APIs/types/functions: `FusePermissionOption` is a clap `ValueEnum` with `AllowOther` and `AllowRoot`, both rendered in snake_case.

Control flow: parsed through `FuseOption`, partitioned in `Cli::run_filesystem`, then converted into runner FUSE options via `Into` implementations outside this file.

State and persistence: no state or persistence. These flags affect mount-time access policy.

Dependencies/integration: depends only on clap derive. The help text documents that default access is restricted to the mounting user, and these options relax that behavior.

Risks/test signals: no local tests; coverage is indirect through CLI parsing and runner behavior. Security-sensitive risk is user confusion: `allow_other` broadens filesystem access, so help text should stay explicit.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/permission_option.rs -->
