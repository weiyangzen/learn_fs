# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/ps2epsi

Shell wrapper converting PostScript/EPS into EPSI with preview/header handling.

Main behavior:
- Accepts `file.ps [file.epsi]`; derives `.epsi` output from `.ps`, `.cps`, `.eps`, `.epsf`, or basename.
- Builds a temporary prolog file in `/tmp/ps2epsi$$`.
- Uses `ls -l` plus AWK and source DSC comments to synthesize title/creator/date/for metadata in PostScript definitions.
- Runs Ghostscript with `-sDEVICE=bit` and `ps2epsi.ps` to generate preview support.
- Appends a rewritten EPS body to the output, stripping prior preview and selected DSC header/comment lines, then writes trailer/EOF.

Important details:
- Temporary file is removed after Ghostscript execution.
- Output is appended with `>>`, so caller expectations depend on output path state.
- Environment `USERNAME`/`LOGNAME` contributes to `%%For`.

Filesystem relevance:
- Conversion script using temporary files and shell text filters; no filesystem implementation content.
