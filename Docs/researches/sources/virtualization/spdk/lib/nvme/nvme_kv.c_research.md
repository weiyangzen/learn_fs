# File Research: sources/virtualization/spdk/lib/nvme/nvme_kv.c

This file implements SPDK helpers for NVMe Key Value command set namespaces.

The data accessors return command-set-specific identify data: `spdk_nvme_kv_ns_get_data()` returns `ns->nsdata_kv`, and `spdk_nvme_kv_ctrlr_get_data()` returns `ctrlr->cdata_kv`.

`nvme_kv_cmd_set_key()` encodes keys into command dwords. It asserts the key is non-null and within the allowed length range, records key length in CDW11, copies the first up to 8 key bytes into CDW2/CDW3, and copies the next up to 8 key bytes into CDW14/CDW15.

`nvme_kv_cmd_with_data()` builds Store, Retrieve, and List-style requests with contiguous payloads. It validates key and data pointers/lengths, allocates a contiguous request, sets opcode and NSID, sets CDW10 value/host-buffer size, stores request options in CDW11, encodes the key, and submits. `nvme_kv_cmd_without_data()` does the same for Delete and Exist without a payload.

Public commands are `spdk_nvme_kv_store()`, `spdk_nvme_kv_retrieve()`, `spdk_nvme_kv_delete()`, `spdk_nvme_kv_exist()`, and `spdk_nvme_kv_list()`. List allows a null start key only when start key length is zero, validates non-null output buffer and length, and encodes an optional start key.

The file assumes KV key sizes match SPDK constants and uses contiguous payload allocation only. It does not check whether the namespace CSI is KV; callers are expected to use it only with KV-capable namespaces.
