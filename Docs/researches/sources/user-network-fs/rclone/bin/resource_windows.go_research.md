# sources/user-network-fs/rclone/bin/resource_windows.go

Purpose: Go generate/tool binary that creates Windows `.syso` resource files embedding version metadata and optionally an icon for `rclone.exe` or `librclone.dll`. It uses source-location discovery to default paths into the repository tree.

Control flow parses flags (`binary`, `arch`, `version`, `icon`, `dir`, `syso`), computes output filename, parses semver, chooses Windows file type based on `.exe` or `.dll`, fills `goversioninfo.VersionInfo`, builds/walks it, and writes the `.syso`. State changes are generated `resource_windows_<arch>.syso` files. Dependencies are `goversioninfo`, semver parsing, icon path, and rclone `fs.Version`. Risks include invalid prerelease version parsing if semver library rejects release suffixes, stale icon path, architecture support limited by goversioninfo, and generated files being consumed by later `go build`. Test signal is generation success and Windows binary metadata inspection.
