<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_list.go -->
# sources/user-network-fs/blobfuse2/cmd/mount_list.go

Purpose: `mount list` subcommand that prints currently known Blobfuse2 mount points.

Important APIs/types/functions: Cobra command `mountListCmd`, `common.ListMountPoints`, and `fmt.Println`.

Control flow: call `common.ListMountPoints`; return a wrapped error if listing fails; otherwise print numbered mount paths starting at 1.

State/persistence behavior: read-only command. It does not alter mounts or config.

Dependencies/integration: registered as a child of `mountCmd` and depends on the common mount discovery implementation, likely reading platform mount tables.

Risks/test signals: output format is simple text and may be consumed by users/scripts. Errors are only as precise as `common.ListMountPoints`. There is no dedicated test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_list.go -->
