# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-utils.h

## Role

`ocp-utils.h` declares the shared OCP utility interface implemented by `ocp-utils.c`. It exposes the OCP UUID constant, UUID lookup helpers, simple OCP log retrieval, and the TCG activity persistent-event predicate.

## Public API

The header declares:

- `extern const unsigned char ocp_uuid[NVME_UUID_LEN]`
- `ocp_get_uuid_index(struct libnvme_transport_handle *hdl, __u8 *index)`
- `ocp_find_uuid_index(struct nvme_id_uuid_list *uuid_list, __u8 *index)`
- `ocp_get_log_simple(struct libnvme_transport_handle *hdl, enum ocp_dssd_log_id lid, __u32 len, void *log)`
- `ocp_is_tcg_activity_event(struct nvme_persistent_event_entry *pevent_entry_head, __u16 el, __u16 vsil)`

The comments describe return behavior for UUID lookup: zero on success, positive NVMe command result from UUID-list retrieval, or negative POSIX-style errors otherwise.

## Dependencies and Integration

The file includes `nvme.h` for libnvme and NVMe structure/type visibility. It references `enum ocp_dssd_log_id`, which is provided by OCP plugin headers included by users of this header in the broader plugin code.

## Notable Risks

The prototype for `ocp_get_log_simple()` is a long single line and depends on the OCP DSSD log-id enum being visible at the point of use. There are no inline guards for misuse beyond normal C type checking.
