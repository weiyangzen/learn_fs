# sources/test-tools/syzkaller/tools/syz-minconfig/minconfig.go

## Purpose
`syz-minconfig` is a manual helper for checking kernel config minimization. It minimizes a full config relative to a base config while preserving a predicate that specified config symbols remain enabled.

## Important APIs, types, and functions
- Flags specify kernel source directory, base config, full config, comma-separated config symbols, and target arch.
- `main` parses Linux Kconfig with `kconfig.Parse`, loads base/full configs with `kconfig.ParseConfig`, defines the predicate, creates a `debugtracer.GenericTracer`, runs `kconf.Minimize`, and writes the serialized minimized config.

## Control flow
After argument parsing, the tool loads the target Kconfig tree from `<sourcedir>/Kconfig`. The predicate iterates `strings.SplitSeq(*flagConfigs, ",")` and returns false if any requested symbol is `kconfig.No`. `Minimize` drives the search and logs trace output to stdout before the final serialized config is also written to stdout.

## State and persistence behavior
The tool reads Kconfig and config files. It writes only stdout and has no persistent output file flag. The minimization predicate is stateless apart from requested config symbol names.

## Dependencies and integration points
It integrates with `pkg/kconfig` minimization logic, `pkg/debugtracer` for trace logging, `pkg/tool` for failures, and `sys/targets` for Linux target metadata.

## Risks and edge cases
No explicit flag validation means empty paths or unknown architecture can fail inside `kconfig.Parse`. Trace and final config share stdout, which is useful manually but awkward for scripts that expect only config content. Empty config names from a trailing comma are not filtered.

## Test signals
No direct tests. The underlying minimizer should be covered in `pkg/kconfig`; this wrapper is best tested with a tiny synthetic Kconfig tree and known base/full configs.
