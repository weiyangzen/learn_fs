# File Research: sources/windows/reactos/drivers/filesystems/mup/mup.h

This is the private MUP header. It includes WDM/NTIFS, PSEH, MUP NDK types, section attributes, and DFS declarations.

It defines helper macros, allocation tag `TAG_MUP`, node type/status constants, and internal node structures:
- `MUP_VCB`: root MUP volume context and share access.
- `MUP_FCB`: MUP file context with associated file object and CCB list.
- `MUP_CCB`: per-provider open context for forwarded operations.
- `MUP_MIC`: master I/O context for fan-out write completion.
- `MUP_UNC`: registered or pending UNC provider state.
- `MUP_PFX`: cached accepted prefix and provider association.
- `MUP_MQC`: master query context for provider prefix-resolution fan-out.
- `FORWARDED_IO_CONTEXT` and `QUERY_PATH_CONTEXT`: per-lower-IRP contexts.

Research notes:
- The node header fields are repeated in every structure rather than embedded as a common base struct.
- `MUP_UNC` carries both registration metadata and opened device/file object references.
- Prefix nodes track whether the accepted-prefix buffer is externally allocated and whether the node is present in the prefix table.
