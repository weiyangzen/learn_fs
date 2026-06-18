## sources/security-integrity/cryfs/crates/cli-utils/src/path.rs

Purpose: provides a clap value parser that converts user-supplied paths into absolute paths.

Important APIs and functions: `parse_path(s: &str) -> Result<PathBuf, String>` calls `Path::new(s).absolutize()`, returns the owned absolute path, and converts path-absolutize errors into strings suitable for clap.

Control flow and state: no persistent state exists. The function resolves relative paths against the process current working directory at parse time.

Dependencies and integration: depends on `path_absolutize` and standard `Path`/`PathBuf`. The doc comment shows use as `#[arg(value_parser=parse_path)]` in clap-derived args.

Risks and test signals: TODO notes missing tests. Absolutization is not canonicalization, so it does not require path existence and does not resolve all symlinks; this is useful for CLI parsing but later code must still validate vault/mount directory accessibility.
