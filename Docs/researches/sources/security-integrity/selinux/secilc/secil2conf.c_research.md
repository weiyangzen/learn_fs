# sources/security-integrity/selinux/secilc/secil2conf.c

Purpose: `secil2conf` is a small command-line converter from one or more SELinux CIL files to textual `policy.conf`. It configures a `cil_db`, adds each input file, compiles the database, and emits the result through `cil_write_policy_conf`.

Important APIs and flow: `usage` documents `-o`, `-M`, `-P`, `-Q`, `-v`, and `-h`. `main` parses options with `getopt_long`, maps MLS strings to `cil_set_mls`, toggles tunable and qualified-name handling, and disables generated attribute expansion with `cil_set_attrs_expand_generated(db, 0)` and size expansion with `cil_set_attrs_expand_size(db, 0)`. Each file is read via `fopen`, `stat`, `malloc`, `fread`, then passed to `cil_add_file`; after all files are added, `cil_compile` runs before opening `policy.conf` or the requested output file.

State and persistence: the only persistent output is the generated policy.conf text; all CIL state is transient inside `cil_db`. Dependencies are libc, `getopt`, `stat`, and libsepol/libcil headers. Risks: whole-file `uint32_t file_size` truncates very large inputs, empty files cause `malloc(0)`/`fread(..., 0, 1)` edge behavior unlike `secilc.c`, and `strdup` results are not checked. Test signals should validate option parsing, multiple input ordering, qualified-name mode, MLS override, output-path failures, and empty-file behavior.
