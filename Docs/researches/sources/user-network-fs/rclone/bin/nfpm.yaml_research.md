# sources/user-network-fs/rclone/bin/nfpm.yaml

Purpose: nfpm package template used by `cross-compile.go` to build Linux `.deb` and `.rpm` artifacts. Template fields `{{.Arch}}` and `{{.Version}}` are substituted into package metadata.

Content maps the built `rclone` binary to `/usr/bin/rclone`, manual/readme files to `/usr/share/doc/rclone`, and `rclone.1` to the manpage path. State is not mutated by this template itself; generated per-build copies are placed in release build directories. Dependencies are nfpm's YAML schema and the artifact layout created by cross-compilation. Risks include package metadata drift, missing license/changelog fields if distro policy requires them, and template/schema incompatibility with nfpm upgrades. Test signal comes from successful package builds and installation checks.
