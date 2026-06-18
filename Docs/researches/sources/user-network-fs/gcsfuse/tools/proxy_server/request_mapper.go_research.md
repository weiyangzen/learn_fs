# sources/user-network-fs/gcsfuse/tools/proxy_server/request_mapper.go

Purpose: maps incoming HTTP requests to proxy retry request types and emulator instruction names.

Important APIs/types/functions: `RequestType` constants, `RequestTypeAndInstruction`, `deduceRequestTypeAndInstruction`, and `isJsonAPI`.

Control flow: JSON API paths containing `/storage/v1` are classified by HTTP method and path shape: GET ending `/o` lists, GET containing `/o/` stats, POST creates, DELETE deletes, PUT updates. Non-JSON GET requests are XML reads. Unknown methods map to `Unknown` with empty instruction.

State/persistence behavior: stateless classification only.

Dependencies/integration: feeds `AddRetryID` and `OperationManager`.

Risks/test signals: JSON read requests are explicitly TODO and currently indistinguishable from stat GETs. Path matching is substring/suffix based and may misclassify unusual encoded paths.
