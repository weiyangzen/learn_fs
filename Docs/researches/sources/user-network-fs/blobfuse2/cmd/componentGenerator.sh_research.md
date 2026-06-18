<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/componentGenerator.sh -->
# sources/user-network-fs/blobfuse2/cmd/componentGenerator.sh

Purpose: developer-only generator for adding a new Blobfuse2 pipeline component from `internal/component.template` and then regenerating blank-import registration in `cmd/imports.go`.

Important APIs/types/functions: shell parameter `$1`, derived variables `comp_name`, `comp_name_C`, `comp_path`, and `comp_file`; template copy from `./internal/component.template`; `sed -i` replacement of `<component>` and `<component_C>`; and delegation to `./cmd/importGenerator.sh`.

Control flow: print a banner, normalize the component name into a Go-style class name, fail if `./component/<name>` already exists, create the component directory, copy the template into `<name>.go`, replace placeholders, then regenerate component imports.

State/persistence behavior: creates a new `component/<name>/<name>.go` file and mutates `cmd/imports.go` through the import generator. It does not roll back partial changes if placeholder replacement or import regeneration fails.

Dependencies/integration: assumes it is executed from the repository root, uses GNU-style `sed -r` and `${1^}` capitalization, and depends on `internal/component.template` matching the placeholder contract. The hidden Cobra `generate` command wraps this script.

Risks/test signals: whitespace or unusual component names can break paths/imports. The script uses `exit` without an explicit nonzero status when a component exists, so callers may treat that failure as success. There are no tests in this subset; success is visible through the generated component and updated imports compiling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/componentGenerator.sh -->
