# sources/test-tools/syzkaller/vm/gce/tar_go1.10.go

## Purpose

`tar_go1.10.go` provides the Go 1.10+ implementation of tar header formatting for GCE image uploads.

## Important APIs, Types, and Functions

It defines `setGNUFormat(hdr *tar.Header)`, which sets `hdr.Format = tar.FormatGNU`.

## Control Flow

`uploadImageToGCS` in `gce.go` calls `setGNUFormat` before writing the disk image tar header. On Go versions matching the build tag, this direct format assignment is used.

## State and Persistence Behavior

The function mutates only the provided tar header before it is written to the gzip/tar stream. The persisted effect is a GNU-format tar member in the uploaded image archive.

## Dependencies and Integration Points

It depends on the standard `archive/tar` package and Go build tags. It pairs with `tar_go1.9.go` for older toolchains.

## Risks and Test Signals

Risk is low; the main compatibility requirement is that GCE accepts the uploaded tar format. Tests should verify generated image archives contain a GNU-format `disk.raw` header under supported Go versions.
