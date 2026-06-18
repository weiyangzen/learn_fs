# sources/test-tools/strace/m4/gen_bpf_attr_m4.awk

Purpose: gawk extractor that reads `src/bpf_attr.h` and emits member references for an Autoconf `AC_CHECK_MEMBERS` probe of `union bpf_attr` fields.

Important APIs/types/functions: uses awk regex matching, `match()` capture arrays, state variable `in_struct`, `struct_name`, optional `subtype_name`, and a generated `prefix` that is either `union bpf_attr`, `struct <name>`, or a subtype-qualified path.

Control flow: when a line starts a generated `struct *_struct` block, it records the structure and optional comment subtype, then enters struct mode. In struct mode it matches simple field declarations and prints a tab-indented `prefix.field,` entry. On the closing brace it leaves struct mode.

State and persistence behavior: has only streaming awk state and writes to stdout. It assumes the input header follows the project generator's predictable struct declaration style.

Dependencies and integration points: invoked by `gen_bpf_attr_m4.sh`; output is sorted and wrapped into `m4/bpf_attr.m4`, which is consumed by configure to detect available Linux BPF attribute members.

Risks: regex parsing is intentionally narrow and may miss bitfields, arrays with unusual declarations, nested constructs, or formatting changes. Incorrect member paths can break configure probes or silently omit capability checks.

Test signals: rerunning `m4/gen_bpf_attr_m4.sh` after BPF header changes, Autoconf `AC_CHECK_MEMBERS` success, and generated `bpf_attr.m4` diffs are the main validation signals.
