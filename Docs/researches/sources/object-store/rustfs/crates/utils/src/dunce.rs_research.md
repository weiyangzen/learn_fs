# sources/object-store/rustfs/crates/utils/src/dunce.rs

Purpose: Windows path simplification utilities adapted from the `dunce` behavior: convert safe verbatim disk paths such as `\\?\C:\...` to ordinary paths.

Important APIs: `simplified`, `canonicalize`, `is_simplified`, and hidden alias `realpath`. Helper functions validate Windows filenames, detect reserved DOS device names, and attempt prefix stripping.

Control flow: On non-Windows, `simplified` is a no-op and `canonicalize` delegates to `fs::canonicalize`. On Windows, `canonicalize` resolves the path then simplifies only safe verbatim disk paths. Simplification rejects non-UTF-8 paths, invalid/reserved names, `..` components, other UNC forms, and paths over MAX_PATH limits.

State and dependencies: Stateless. Uses platform cfgs, std filesystem/path APIs, and Windows-only path component matching.

Integration points: Enabled by utils `os` feature; useful when passing canonical paths to tools that do not accept verbatim UNC paths.

Risks and tests: Strict UTF-8 and MAX_PATH checks intentionally leave many paths unchanged. Tests cover reserved names, filename validity, Windows simplification under cfg, Unix no-op behavior, and `is_simplified`.
