# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixlink.mak

Common Unix interpreter link fragment.

Key points:
- Defines `UNIXLINK_MAK`.
- Uses `.NOEXPORT` to avoid huge environment-expanded command lines on limited System V systems.
- Defines interpreter archive objects and final executable object list.
- Provides `$(GS).a` archive target for the complete interpreter, though not used by standard builds.
- Defines final `$(GS_XE)` link step by writing a shell script/trailer with `echogs`, concatenating `ld.tr`, and appending extra and standard libraries.
- Sets `LD_RUN_PATH` when `XLIBDIR` is present.
- Clears large make variables in the environment during final shell execution to work around SCO Unix limits.

Dependencies and interactions:
- Consumes object/link traces produced by earlier make fragments.
- Included by Unix top-level makefiles after device and interpreter object lists are known.

Research relevance:
- Shows how Ghostscript avoided command-line length and environment limitations in legacy Unix final linking.
