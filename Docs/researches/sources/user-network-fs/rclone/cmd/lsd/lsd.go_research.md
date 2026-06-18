# sources/user-network-fs/rclone/cmd/lsd/lsd.go

Purpose: implements `rclone lsd`, listing directories/containers/buckets with size, modtime, object count, and name.

Important APIs/state: package global `recurse`; Cobra command with `--recursive/-R`; `operations.ListDir`. When recursive is requested it sets `fs.GetConfig(ctx).MaxDepth = 0`.

Control flow: validates one source arg, optionally changes global config max depth, builds source Fs, and runs `operations.ListDir` to stdout.

State/persistence: read-only remote listing and stdout output, but it mutates the process-wide config `MaxDepth` for recursive behavior. Dependencies include command root, list help, `fs.GetConfig`, flags, and operations. Risks include global config mutation during tests/concurrent command contexts and backend directory-count uncertainty. Test signals are likely indirect via operations.
