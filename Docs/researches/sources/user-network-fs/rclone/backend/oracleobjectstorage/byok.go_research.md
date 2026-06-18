# sources/user-network-fs/rclone/backend/oracleobjectstorage/byok.go

Purpose: handles Oracle Object Storage bring-your-own-key and SSE-C/SSE-KMS option validation and request header population. It is compiled only on supported non-Plan9, non-Solaris, non-JS platforms.

Important APIs: `validateSSECustomerKeyOptions` rejects mutually exclusive KMS and customer-key settings and delegates to `populateSSECustomerKeys`. `populateSSECustomerKeys` reads a base64 AES key from `SSECustomerKeyFile` or `SSECustomerKey`, decodes it, computes a base64 SHA256 checksum, validates or fills `SSECustomerKeySha256`, and defaults `SSECustomerAlgorithm` to `AES256`. `useBYOKPutObject`, `useBYOKHeadObject`, `useBYOKGetObject`, and `useBYOKCopyObject` copy relevant option values into OCI SDK request structs.

Control flow: `NewFs` in the main backend calls `validateSSECustomerKeyOptions` before creating the OCI client. Upload preparation calls `useBYOKPutObject`; object metadata and downloads call `useBYOKHeadObject` and `useBYOKGetObject`; server-side copy calls `useBYOKCopyObject`. KMS key IDs are used for put/copy, while SSE-C customer headers are needed for put/head/get/copy.

State and persistence behavior: mutates the in-memory `Options` during setup by populating key, checksum, and algorithm fields. It reads key material from local disk when configured. The persistent remote effect is server-side encryption metadata/behavior on OCI objects.

Dependencies and integration points: uses standard crypto/base64/os/string helpers and OCI SDK `common` and `objectstorage` request types. It relies on `expandPath` from `client.go` for `~` expansion.

Risks: key material is sensitive and is stored in `Options` as strings after loading. Error text for decoding always mentions `sse_customer_key_file` even if the inline key was used. Misconfigured checksum blocks startup, which is appropriate for integrity but can be user-visible. SSE headers must be kept in sync across put, multipart create/part, head, get, and copy paths or encrypted objects may become unreadable.

Test signals: no direct tests in this subset. Behavior is indirectly covered only if Oracle integration tests run with SSE options.
