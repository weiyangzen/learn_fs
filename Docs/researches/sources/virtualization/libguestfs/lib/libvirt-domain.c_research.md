# File Research: sources/virtualization/libguestfs/lib/libvirt-domain.c

Implements adding disks from an existing libvirt domain.

Important behavior:
- `guestfs_impl_add_domain` opens libvirt, locates the domain by UUID optionally and then by name, and forwards selected options to `guestfs_add_libvirt_dom_argv`.
- Live access is removed and explicitly rejected.
- `guestfs_impl_add_libvirt_dom` refuses writable access to running VMs, preventing disk corruption.
- Reads libvirt XML with `virDomainGetXMLDesc` and parses it with libxml2 using `XML_PARSE_NONET`.
- Extracts SELinux `seclabel`/`imagelabel` and passes them to backend settings before disks are added.
- Checkpoints drive state so either all domain disks are added or the previous drive list is restored.
- Handles disk XML types `file`, `block`, `network`, and `volume`.
- Network disk parsing supports source protocol/name, hosts, optional auth username, libvirt secrets by UUID or usage, and base64 encoding for Ceph secrets.
- Volume disks resolve storage pool and volume names to file paths, supporting only file-based libvirt volumes.
- Honors `readonlydisk` policy: `error`, `read`, `write`, or `ignore`.
- Extracts driver format, readonly flag, and logical block size.

Filesystem relevance:
- Converts libvirt domain storage definitions into libguestfs drives, preserving read-only safety, block size, network storage credentials, and SELinux context handling.
