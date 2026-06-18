<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/tests/arguments.rs -->
# sources/security-integrity/cryfs/crates/cli-utils/tests/arguments.rs

Purpose: integration-style tests for `cryfs-cli-utils::run` and its clap `Application` wrapper. The file dynamically builds small temporary Rust binaries with `tempproject`, then verifies common argument behavior across empty args, flags, mandatory/optional positionals, mandatory/optional options, help, version, and debug-build warnings.

Important APIs/types/functions: `TestConfig::project` generates a Cargo project and main program using `Application`; `TestProject::expect_help_message` centralizes help assertions; static `PROJECT_*` fixtures are wrapped in `StaticDrop` so temp dirs are cleaned at process exit. Tests use `assert_cmd`, `predicates`, `rstest`, `lazy_static`, and `indoc`.

Control flow: each fixture builds a binary once, then modules run combinations of CLI arguments. Help wins over other args, version is exclusive with other real args, parsing errors still include the version banner, and debug/release builds differ in warning output.

State and persistence: creates temporary Cargo projects and binaries; the explicit cleanup wrapper prevents leaked temp directories from long-lived statics.

Dependencies/integration: exercises `cryfs-cli-utils` through a real generated binary rather than direct unit calls, so it covers clap integration, logging defaults, version emission, and debug-build warning plumbing.

Risks/test signals: tests are broad but expensive because they compile temp projects. They intentionally rely on exact clap error text and may need updates when clap formatting changes. No subcommand coverage yet; a TODO records that gap.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/tests/arguments.rs -->
