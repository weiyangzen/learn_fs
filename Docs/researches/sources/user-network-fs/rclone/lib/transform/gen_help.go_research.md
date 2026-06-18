# sources/user-network-fs/rclone/lib/transform/gen_help.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/gen_help.go -->
## sources/user-network-fs/rclone/lib/transform/gen_help.go

Purpose: go-generate helper for producing `transform.md` help text from the current transform choices, charmap choices, encoder masks, command descriptions, and generated examples. It is excluded from normal builds with `//go:build none`.

Important APIs and control flow: local `commands` and `example` structs back `commandList` and `examples`. `example.command()` formats an example `rclone convmv` invocation. `example.output()` sets transform options in a background context and runs `transform.Path`. `SprintList()` builds a markdown table, conversion mode list, charmap list, encoding mask list, and examples. `main()` writes the generated help to stdout or a path argument with a generated-file banner.

State, dependencies, and integration: depends on `context`, `fmt`, `os`, `strings`, rclone `fs`, `encoder`, and `transform`. It integrates through the `go:generate` directive in `transform.go`.

Risks and test signals: generated examples execute real transform code, so a transform behavior bug can be embedded into help. `os.Create` errors are fatal through `fs.Fatalf`; close errors are ignored. No direct tests are included.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/gen_help.go -->
