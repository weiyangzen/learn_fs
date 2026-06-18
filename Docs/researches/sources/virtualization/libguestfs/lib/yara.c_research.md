# File Research: sources/virtualization/libguestfs/lib/yara.c

Host-side wrapper for YARA scan results.

Important behavior:
- `guestfs_impl_yara_scan` asks the daemon to scan a guest path and write serialized detections to a temp file.
- Parses the temp file into `guestfs_yara_detection_list`.
- Result arrays start at length 8 and double when full.
- Each detection entry is zeroed before XDR decode.
- XDR decode failures are reported and partial results are freed.
- Final list length is the number of decoded detections.

Filesystem relevance:
- Converts appliance-side malware/signature scan results over guest filesystems into public host-side result structures.
