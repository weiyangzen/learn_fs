<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryInformationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryInformationHelper.cs

Purpose: Maps SMB1 file query information levels to shared FSCC classes and performs bidirectional conversion between shared `FileInformation` DTOs and SMB1 query structures.

Important APIs/types/functions: `ToFileInformationClass`, `FromFileInformation`, `ToFileInformationLevel`, and `ToFileInformation` cover basic, standard, EA, name, all, alternate-name, stream, and compression information.

Control flow: Enum switches choose information classes. Type dispatch copies fields into equivalent wire DTOs; composite `FileAllInformation` is flattened to or assembled from nested basic, standard, EA, and name objects.

State and persistence behavior: No persistence; conversions allocate new objects and copy timestamps, attributes, allocation sizes, flags, stream entries, compression fields, and names.

Dependencies and integration points: Sits between SMB1 transaction handlers and shared filesystem abstractions. It depends on `FileInformation`, stream entries, compression enums, `ExtendedFileAttributes`, and SMB1 query DTO serializers.

Risks and edge cases: Unrecognized subclasses throw `NotImplementedException`. Attribute enum casts assume overlapping SMB1/shared bit values. Stream entries are shallow-copied via `AddRange`, so mutable entry objects are shared.

Test signals: Tests should verify bidirectional round trips for all supported classes, `FileAllInformation` composition, stream list behavior, compression reserved bytes, and unsupported-level exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryInformationHelper.cs -->
