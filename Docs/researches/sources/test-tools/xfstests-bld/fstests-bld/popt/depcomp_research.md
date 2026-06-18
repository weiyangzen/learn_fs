# sources/test-tools/xfstests-bld/fstests-bld/popt/depcomp

## Purpose

`depcomp` is the Automake dependency-compilation wrapper vendored with the `popt` subtree inside xfstests-bld. It runs the compiler command supplied on its argv, collects compiler-generated dependency side effects, normalizes them into the dependency file named by `depfile`, and adds dummy header targets so generated make dependency includes do not fail after a header is deleted.

The source was read as a complete 630-line shell script. It is generated Autotools infrastructure rather than project-specific business logic, but it is on the critical build path for compiling the vendored `popt` library on many compilers and host platforms.

## Important APIs, Types, and Functions

The script's public interface is its command-line and environment contract:

- `depcomp [--help] [--version] PROGRAM [ARGS]` executes `PROGRAM ARGS`.
- Required environment variables are `depmode`, `source`, and `object`.
- Optional environment variables are `DEPDIR`, `depfile`, `tmpdepfile`, `libtool`, `MAKEDEPEND`, and compiler/tool variables inherited through `PROGRAM ARGS`.
- Generated defaults map an object such as `sub/bar.o` to `sub/.deps/bar.Po`; `tmpdepfile` is the same path with `.T*` suffix.

Supported `depmode` values include `gcc3`, `gcc`, `hp`, `sgi`, `aix`, `icc`, `hp2`, `tru64`, `dashmstdout`, `dashXmstdout`, `makedepend`, `cpp`, `msvisualcpp`, `msvcmsys`, and `none`. Compatibility aliases are normalized before the main `case`: `hp` becomes `gcc` with `gccflag=-M`, `dashXmstdout` becomes `dashmstdout` with `dashmflag=-xM`, and `msvcmsys` becomes `msvisualcpp` with a `sed`-based path converter instead of `cygpath`.

Important shell transformations are the `sed`, `tr`, `sort`, and `cygpath`/path-conversion pipelines that rewrite compiler-native dependency output into Makefile-compatible rules. There are no functions; each depmode stanza is a top-level branch.

## Control Flow

Startup handles empty command, `--help`, and `--version`, then validates that `depmode`, `source`, and `object` are set. It computes `depfile` and `tmpdepfile`, deletes any stale temporary dependency file, normalizes alias modes, and dispatches through the single large `case "$depmode"`.

The common control-flow shape is:

1. Invoke the compiler command with depmode-specific dependency flags or run it once before a second dependency-only pass.
2. Check the command status; on failure, remove temporary dependency files and exit with the compiler status.
3. Rewrite compiler-generated dependency output so the target is the configured `$object`.
4. Append dummy `header.h:` style rules for each dependency where the compiler mode can expose deleted-header failures.
5. Remove temporary files and exit successfully.

Fast GCC3 mode injects `-MT "$object" -MD -MP -MF "$tmpdepfile"` immediately before the `-c` argument, runs the compiler once, and renames the temporary file to the final dependency file. Older `gcc` mode uses `-Wp,-MD,...`, rewrites the target manually, and generates dummy targets. Vendor-specific modes locate compiler-specific side-effect files such as AIX `.u`, HP `foo.d`, Tru64 `.o.d`, or libtool `.libs` variants before rewriting them. `dashmstdout`, `cpp`, and `msvisualcpp` remove libtool wrappers and `-o $object` arguments, run preprocessing to stdout, and derive dependency lists from preprocessor line markers. `makedepend` strips unsupported compiler options and delegates to `${MAKEDEPEND-makedepend}`. `none` simply `exec`s the compiler command with no dependency tracking.

## State and Persistence Behavior

Persistent outputs are the final dependency file at `$depfile` and the object or compilation side effects produced by the compiler command. Transient files include `$tmpdepfile` and depmode-specific compiler byproducts such as `.u`, `.d`, `.o.d`, and `.libs/*` dependency files. The script removes temporary dependency files on successful paths and on most compiler failures.

The wrapper has no internal persistent state across invocations. Its behavior is entirely determined by environment variables, the compiler command, current working directory, filesystem layout, and tool availability. Because Makefile includes often read `*.Po`/`*.Plo` files incrementally, incomplete or stale dependency files can persist into later builds if a depmode branch fails after creating `$depfile`.

## Dependencies and Integration Points

`depcomp` integrates with Automake-generated make rules and Autoconf's dependency-mode selection. `depend.m4` expects some unreachable branch labels to exist textually, so placeholder cases such as `hp`, `dashXmstdout`, and `msvcmsys` must remain in the script even though pre-dispatch normalization prevents them from running.

The script depends on `/bin/sh`, `sed`, `tr`, `sort`, `rm`, `mv`, optional `cygpath`, optional `makedepend`, the selected compiler, and libtool argument conventions when `libtool=yes`. It is consumed by `Makefile.in`-generated compile rules for the `popt` subtree, where `$object`, `$source`, `$DEPDIR`, and `$depmode` are set by Automake.

## Risks and Edge Cases

The script is portable shell from 2009, so its quoting and text processing intentionally target old systems but still carry edge-case risk with unusual filenames. Dependency parsing is largely whitespace-oriented; paths with spaces, tabs, embedded newlines, colons, or backslashes can be misparsed, though the script has special handling for DOS drive-letter paths in some modes. Several branches rely on compiler output formats that may vary by version or vendor.

The `gcc` and aligned parser branches create dummy header rules to tolerate deleted headers, but correctness depends on the dependency list being parsed accurately. Some modes write `#dummy` if no compiler dependency file appears, which keeps Makefile includes from failing but can hide missing dependency tracking. The script deliberately removes and rewrites `$depfile`; interruption between those steps can leave a missing or partial dependency file. `none` mode bypasses tracking completely and can cause stale builds if used accidentally.

## Test Signals

Useful build signals include running `./configure` for the `popt` subtree and confirming the selected dependency mode, then compiling with `make V=1` to verify `depcomp` invocations create `.deps/*.Po` or `.Plo` files. Regression tests should cover default GCC/GCC3 flows, `libtool=yes` object names, dependency files for subdirectory objects, deleted-header rebuild behavior, missing compiler failure cleanup, `depmode=none`, and path conversion behavior on MSYS/Cygwin-style paths. A practical smoke test is to touch a header included by a `popt` C file and confirm the object rebuilds, then delete that header from the dependency file context and confirm make reports the real source failure rather than an include-file dependency parse error.
