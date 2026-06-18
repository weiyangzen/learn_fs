# sources/object-store/garage/src/garage/cli/local/completions.rs

Purpose: generates shell completions for the Garage CLI.

Important APIs/types/functions: `generate_completions(shell: Shell)`.

Control flow: obtains the structopt/clap command from `Opt::clap()`, captures the command name, and writes completions for the requested shell to stdout.

State and persistence: no persistent state; stdout output only.

Dependencies and integration points: uses `structopt::{clap::Shell, StructOpt}` and crate root `Opt`. Invoked by local CLI command dispatch.

Risks: depends on the full CLI definition being represented by `Opt`. Changes in structopt/clap generation behavior may alter completion output.

Test signals: no direct tests; compile-time coverage and manual completion generation are primary checks.
