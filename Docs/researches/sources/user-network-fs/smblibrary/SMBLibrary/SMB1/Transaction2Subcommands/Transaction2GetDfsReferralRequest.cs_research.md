# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2GetDfsReferralRequest.cs

- **Purpose:** TRANS2_GET_DFS_REFERRAL Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1365 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2GetDfsReferralRequest`.
- **Important APIs/types/functions:** Types: class Transaction2GetDfsReferralRequest : Transaction2Subcommand. Constructors: Transaction2GetDfsReferralRequest. Constants/static metadata: none. Fields/properties: ReferralRequest. Methods/overrides: GetSetup, GetParameters. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_GET_DFS_REFERRAL.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: SMBLibrary.DFS, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
