# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2epsi

Shell wrapper that produces EPSI from PostScript.

Behavior:

- Accepts `file.ps [file.epsi]`; derives `.epsi` from common PostScript/EPS suffixes when omitted.
- Creates a temporary metadata file in `/tmp/ps2epsi$$`.
- Uses `ls -l` plus AWK and the input’s DSC comments to synthesize PostScript variables for title, creator, creation date, and user.
- Runs Ghostscript at 72 dpi with the `bit` device and `ps2epsi.ps` to generate preview metadata, redirecting Ghostscript output to stderr.
- Rewrites the final EPSI by emitting a prolog/trailer wrapper around the original input with old preview and selected DSC boilerplate stripped by `sed`.

It is document-conversion shell glue with temporary-file handling.
