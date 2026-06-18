# sources/test-tools/syzkaller/tools/syz-fmt/syz-fmt.go

Purpose: `syz-fmt` formats syzkaller syscall description `.txt` files into canonical AST formatting.

Important APIs and flow: `main` accepts files, directories, or `all`; `all` expands to every `sys/<os>` directory. Directories are scanned for `.txt` files. `processFile` reads a file, parses it with `ast.Parse`, formats it with `ast.Format`, and either reports dry-run failure or renames the original to `file~` and writes formatted content with the original mode.

State and persistence: modifies description files in place unless `-dry-run` is set; creates backup files with `~` suffix.

Dependencies and integration: uses syzkaller AST parser/formatter, OS target list, `osutil.Rename`, and `tool.Init`.

Risks: parse errors exit the process. Backup rename plus write is not atomic as a combined operation, and stale `file~` handling depends on `osutil.Rename`. Directory mode only processes immediate `.txt` children.

Test signals: no direct test here; AST formatting tests cover core behavior. Dry-run exit code 2 is the CI-friendly signal for formatting drift.
