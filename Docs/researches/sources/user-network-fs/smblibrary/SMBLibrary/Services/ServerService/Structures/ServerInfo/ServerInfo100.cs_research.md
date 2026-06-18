<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo100.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo100.cs

## Purpose
NDR structure for MS-SRVS `SERVER_INFO_100`, carrying platform ID and server name.

## APIs, Types, and Functions
Fields are `PlatformName PlatformID` and `NDRUnicodeString ServerName`. It implements `Read()`, `Write()`, and `Level => 100`.

## Control Flow, State, and Persistence
Constructor initializes `ServerName`. Read/write wrap structure boundaries and use embedded full pointers for the string. No persistence.

## Dependencies and Integration
Used by `ServerService` level-100 server info responses and by `ServerInfo`.

## Risks and Test Signals
Risks include null `ServerName` if parser or caller does not initialize it and platform values not matching host reality. Test NDR round trips and Windows client display of level-100 info.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo100.cs -->
