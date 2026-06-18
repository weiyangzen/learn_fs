# File Research: sources/virtualization/nbdkit/plugins/cdi/cdi.c

This plugin exports one layer from a container image as a read-only block device. It accepts `name` as a required image name/URI and `layer` as an index, including negative indexes interpreted by the shell/JQ expression.

At `.get_ready`, `make_layer` creates a temporary file, constructs a shell script with quoted variables, runs `podman pull`, saves the image as a Docker directory, uses `jq` and `cut` to find the selected layer digest in `manifest.json`, moves that layer file over the temporary file, removes the extracted directory, reopens the resulting file read-only with `O_CLOEXEC`, and unlinks it.

Runtime callbacks need no per-connection handle. Size is determined by `device_size(fd)`, data is served with a robust `pread` loop, multi-conn is true, and cache is emulated through reads.

Risks and invariants: runtime depends on external `podman`, `jq`, shell, temporary storage, and enough disk space for the saved image. The exported file descriptor is global and closed at unload. The plugin is read-only and parallel-safe because all clients read the same immutable fd.
