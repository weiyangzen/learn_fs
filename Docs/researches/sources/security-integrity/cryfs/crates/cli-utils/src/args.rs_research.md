## sources/security-integrity/cryfs/crates/cli-utils/src/args.rs

Purpose: shared clap argument parsing with special handling for `--version` as an immediate-exit flag that should work even when concrete application args are absent.

Important APIs and types: `ImmediateExitFlags` contains `version`. `CombinedArgs<ConcreteArgs>` flattens immediate flags, concrete args, and `LogArgs`. `ParseArgsResult` distinguishes `ShowVersion` from normal parsed args. `ArgParseError` separates clap display/parse errors from custom `CliError`s.

Control flow and state: `parse_args` first tries to parse only immediate flags. If `--version` is present alone, it returns `ShowVersion`. Help errors are re-parsed against full args so clap can produce full help. Unknown arguments trigger full parse and a custom invalid-argument error if `--version` was combined with normal arguments.

Dependencies and integration: uses `clap` derive/builders, `clap_logflag`, and `CliErrorKind::InvalidArguments`. `clap_style` customizes help colors.

Risks and test signals: parsing depends on clap error-kind behavior; TODOs note unreachable-looking branches. The important security/usability signal is rejecting `--version` mixed with operational arguments so immediate-exit behavior cannot be ambiguous.
