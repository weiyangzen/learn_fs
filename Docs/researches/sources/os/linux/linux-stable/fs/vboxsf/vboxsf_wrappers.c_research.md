# File Research: sources/os/linux/linux-stable/fs/vboxsf/vboxsf_wrappers.c

Wraps VirtualBox HGCM shared-folder service calls behind Linux-style helpers returning negative errno values. `vboxsf_connect()` locates the guest device and connects to the `"VBoxSharedFolders"` service, storing a global client id. `vboxsf_disconnect()` closes it. `vboxsf_call()` centralizes guest-device lookup, HGCM invocation, VirtualBox status capture, and status-to-errno conversion.

The remaining functions build typed HGCM parameter structs defined in `shfl_hostintf.h`: map/unmap folder, create/open, close, remove, rename, read, write, directory listing, file/volume information, readlink, symlink, UTF-8 mode, and symlink mode. Read/write/list/fsinfo update in/out byte-count fields after calls.

Important integration details: host create/open may return success while `create_parms->handle` remains nil and the result code explains why, so callers must inspect both errno and returned fields. Directory listing maps the host “no more files” condition to positive `1`, which `utils.c` treats as end-of-directory.
