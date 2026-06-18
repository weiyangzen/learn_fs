# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryResponseSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryResponseSpec.groovy

Purpose: exercises query-directory response parsing from a large captured SMB2 packet. It converts bytes to `SMB2QueryDirectoryResponse`, then decodes `outputBuffer` via `FileInformationFactory.parseFileInformationList` using the `FileIdBothDirectoryInformation` decoder. Assertions include class type, 18 entries, dot and dot-dot names, a normal child entry, and a later garbled-looking Unicode name.

State and persistence: transient buffers only. Dependencies are SMB2 converter, MS-FSCC file-information decoders, and byte utilities. Integration point is directory listing over SMB. Risks covered include chained variable-size directory records, alignment, output-buffer slicing, and Unicode decoding. Test signal is strong for a real-world payload, but expected names are sparse.
