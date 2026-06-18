# File Research: sources/virtualization/qemu/block/rbd.c

Implements the Ceph RADOS Block Device protocol driver. It parses legacy `rbd:pool/image[@snap][:key=value...]` filenames and modern QAPI options, connects to a RADOS cluster, opens an RBD image or snapshot, performs asynchronous I/O through librbd, supports image creation/truncation/discard/flush/write-zeroes where available, exposes snapshots, reports allocation status through fast-diff when possible, and registers as protocol `rbd`.

Connection setup handles monitor hosts, pool, namespace, image, snapshot, user, conf file, auth modes, key secrets, and legacy key/value pairs. Snapshot opens are forced read-only. The driver tracks image name, snapshot name, namespace, image size, object size, and probed/loaded encryption format in `BDRVRBDState`.

Optional librbd encryption support converts QAPI LUKS/LUKS2 options into librbd encryption format/load structures, including layered encryption through `rbd_encryption_load2` when available. If encryption is not requested, the driver probes the first bytes of the image for RBD/LUKS header markers so image-specific info can report likely encryption format.

`qemu_rbd_start_co()` bridges librbd async completions into QEMU coroutines: it creates a completion object, issues the selected read/write/discard/flush/write-zeroes operation, yields, and is woken by a bottom half scheduled from the librbd callback thread. Writes that extend beyond the tracked image size resize first. Short reads are zero-padded.

Block status defaults to allocated data but, when fast-diff is supported and valid, uses `rbd_diff_iterate2()` to distinguish allocated data from holes/zero regions. Older librbd versions get workarounds for non-object-aligned offsets, striping, and cloned images. Snapshot APIs create, delete, roll back, and list RBD snapshots, using the snapshot name as QEMU's snapshot ID.
