# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestOzoneManagerProtocolClientSideTranslatorPB.java

Purpose: tests client-side protobuf translator request construction for `startQuotaRepair`.

Important APIs/types/functions: exercises `OzoneManagerProtocolClientSideTranslatorPB.startQuotaRepair`, `OmTransport.submitRequest`, and protobuf `StartQuotaRepairRequest/Response`, `OMRequest`, `OMResponse`, command type `StartQuotaRepair`, and status `OK`.

Control flow and state: mocked transport returns a successful response. Argument captors inspect outgoing `OMRequest` and verify empty and specified bucket lists are encoded correctly. Null bucket lists throw `NullPointerException` with message containing `buckets == null` and do not call transport.

Dependencies and integration points: uses Mockito and AssertJ. Translator correctness is required for OM admin/repair client APIs.

Risks and test signals: catches wrong command type, bucket list loss, and unintended RPC calls on invalid input. Coverage is narrow but precise for quota repair API contract.
