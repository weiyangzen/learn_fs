# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unixlink.mak

Unix final link makefile fragment.

Key points:
- Uses `.NOEXPORT` to prevent GNU make from exporting all environment variables and overflowing old System V command limits.
- Defines interpreter archive object groups: `INT_ARCHIVE_ALL`, `XE_ALL`.
- Provides optional archive target `$(GS).a` using `ar` and `ranlib`.
- Defines final `$(GS_XE)` link rule by generating a shell/link transcript with `echogs`, appending `ld.tr`, adding extra and standard libraries, and executing it through `$(SH)`.
- Sets `LD_RUN_PATH` when `XLIBDIR` is non-empty.
- Clears many large environment variables before executing the final link for SCO Unix environment-space limits.

Dependencies and interactions:
- Included by Unix top-level makefiles.
- Consumes generated object/link lists from `gs.mak`, `int.mak`, `devs.mak`, and related fragments.

Research relevance:
- Captures how old Ghostscript avoided command-line and environment-size limits during Unix linking.
