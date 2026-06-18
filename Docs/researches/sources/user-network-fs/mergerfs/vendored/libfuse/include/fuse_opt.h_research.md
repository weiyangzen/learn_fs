<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_opt.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_opt.h

Purpose: This is the FUSE option parsing public interface. It describes templates for command-line and `-o` options, an argument-vector container, and functions to parse, add, insert, escape, free, and match options.

Important APIs and types: `struct fuse_opt` maps a template to either a data offset/value assignment or a processor callback key. `FUSE_OPT_KEY` and `FUSE_OPT_END` build option tables. `struct fuse_args` tracks `argc`, NUL-terminated `argv`, and allocation ownership. `fuse_opt_proc_t` lets callers keep, discard, or transform options.

Control flow and state: `fuse_opt_parse` reads input args, applies all matching option templates, mutates caller data by offset or invokes the callback, and writes an output argument vector. Helper functions allocate or free option strings/argument arrays.

Risks and test signals: offset-based writes are inherently unsafe if tables do not match the target struct. `%s` templates allocate strings that callers must later free through the expected path. Tests should cover `-o` comma lists, escaped commas, two-argument options, non-options after `--`, keep/discard keys, parse errors, and repeated parse/free cycles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_opt.h -->
