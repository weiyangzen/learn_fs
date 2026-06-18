# sources/test-tools/strace/m4/gen_bpf_attr_m4.sh

Purpose: shell wrapper that regenerates `m4/bpf_attr.m4` from `src/bpf_attr.h` using the adjacent awk extractor.

Important APIs/types/functions: uses POSIX shell with `-efu`, sets `input=src/bpf_attr.h`, redirects stdout to `m4/bpf_attr.m4`, emits an `AC_DEFUN([st_BPF_ATTR], ...)` body, invokes `gawk -f gen_bpf_attr_m4.awk`, sorts unique member references, and includes `#include <linux/bpf.h>` for the configure probe.

Control flow: writes a fixed m4 header, streams generated members from awk through `sort -u`, then writes a fallback `union bpf_attr.dummy` member and closes the macro.

State and persistence behavior: overwrites the generated m4 file atomically only in the sense of shell redirection at start; an interrupted run could leave a partial file. No temporary file or cleanup is used.

Dependencies and integration points: depends on `gawk`, `src/bpf_attr.h`, and the Autoconf macro consumer. It bridges strace's internal BPF attribute model with configure-time Linux header feature detection.

Risks: direct redirection can truncate output on failure. The script assumes it is run from the repository root and that `${0%/*}` resolves to the `m4` directory.

Test signals: generated `bpf_attr.m4` should contain a normalized `AC_CHECK_MEMBERS` list and configure should detect expected `union bpf_attr` members against current kernel headers.
