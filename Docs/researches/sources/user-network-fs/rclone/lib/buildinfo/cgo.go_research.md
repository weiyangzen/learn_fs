
# sources/user-network-fs/rclone/lib/buildinfo/cgo.go

Purpose: records the `cgo` build tag in build information when compiled with cgo enabled.

Important APIs/types/functions: build tag `cgo`; `init` appends `"cgo"` to package variable `Tags`.

Control flow: Go runtime executes `init` during package initialization only in cgo builds.

State/persistence: mutates in-memory `buildinfo.Tags`.

Dependencies/integration: integrates with `buildinfo/tags.go` and version/build-info display.

Risks: relies on shared mutable `Tags` ordering with other build-tag init files.

Test signals: build output including `cgo` tag when compiled with cgo.
