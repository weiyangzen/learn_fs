# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/ServiceNameHelper.cs

- **Purpose:** Provides shared SMB1 conversion helpers used by command and subcommand serializers. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 50 lines, 1585 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ServiceNameHelper`.
- **Important APIs/types/functions:** Types: class ServiceNameHelper. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: GetServiceString, GetServiceName. Protocol discriminator returns: ServiceName.DiskShare, ServiceName.PrinterShare, ServiceName.NamedPipe, ServiceName.SerialCommunicationsDevice, ServiceName.AnyType. Dispatch cases: ServiceName.DiskShare, ServiceName.PrinterShare, ServiceName.NamedPipe, ServiceName.SerialCommunicationsDevice.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: none.
- **Integration points:** Converts between service enum values and the OEM service strings exchanged by tree-connect packets.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
