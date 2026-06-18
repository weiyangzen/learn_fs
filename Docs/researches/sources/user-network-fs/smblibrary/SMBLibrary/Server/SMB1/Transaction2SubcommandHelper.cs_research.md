# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/Transaction2SubcommandHelper.cs

## Purpose

Implements SMB1 Transaction2 subcommands for directory search, filesystem query/set, path query, file query, and file set information.

## Important APIs, Types, And Functions

`GetSubcommandResponse` overloads handle FindFirst2, FindNext2, QueryFSInformation, SetFSInformation, QueryPathInformation, QueryFileInformation, and SetFileInformation.

## Control Flow

FindFirst queries and caches all entries in `OpenSearch`, returns a segment, and optionally closes at EOS. FindNext pages from cached entries and removes the search at end. Query/set methods choose passthrough or SMB1 information-level conversion, enforce share access, truncate responses to `maxDataCount` with `STATUS_BUFFER_OVERFLOW`, and delegate to file-store helpers.

## State And Persistence Behavior

Mutates open-search state and persistent file/filesystem metadata for set operations. Query operations read backing file-store state.

## Dependencies And Integration Points

Depends on Transaction2 command classes, `SMB1FileStoreHelper`, `FindInformationHelper`, `FileInformation`, `FileSystemInformation`, shares, sessions, and file stores.

## Risks And Edge Cases

Find results are fully materialized and cached, so large directories can consume memory and become stale. `returnResumeKeys` is computed but unused. Access checks are share-type dependent. Buffer overflow truncates response bytes without all callers necessarily expecting partial structures.

## Test Signals

Test find pagination and close flags, invalid SID, unsupported levels, passthrough versus legacy levels, buffer overflow truncation, access denied, malformed set buffers, and file-store status propagation.

Source-read signal: reviewed the complete local source file for this item.
