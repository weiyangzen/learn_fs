# sources/user-network-fs/rclone/lib/plugin/package.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/plugin/package.go -->
## sources/user-network-fs/rclone/lib/plugin/package.go

Purpose: package-level documentation for rclone's optional Go plugin loader. It explains how out-of-tree storage backends can be compiled as `go build -buildmode=plugin` artifacts and loaded through `RCLONE_PLUGIN_PATH`.

Important APIs and control flow: this file declares package `plugin` only. The operational loader is in `plugin.go` behind Linux/macOS build tags. The docs specify the expected file naming convention `librcloneplugin_NAME.so` and require plugin packages to use package name `main`.

State, dependencies, and integration: there is no runtime state. The file keeps unsupported platforms buildable by providing a package file even when the real plugin loader is excluded by build tags. It integrates with the entrypoint and library builds through blank imports of `github.com/rclone/rclone/lib/plugin`.

Risks and test signals: plugin loading is platform- and toolchain-sensitive; Go plugins are not supported everywhere and are excluded for `gccgo` by the implementation file. There are no tests in the requested set for plugin discovery or failed loads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/plugin/package.go -->
