# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenSelector.java

## Purpose
Selects an HDDS block token matching a requested Hadoop token service.

## Important APIs and types
Implements `TokenSelector<OzoneBlockTokenIdentifier>`. `selectToken(Text service, Collection<Token<? extends TokenIdentifier>> tokens)` returns the first token whose kind is `HDDS_BLOCK_TOKEN` and service equals the requested service.

## Control flow and state
The selector is stateless. It returns null for null service or no match. It performs an unchecked cast after matching token kind.

## Dependencies and integration points
Used by Hadoop security token lookup paths for block operations. It depends on `OzoneBlockTokenIdentifier.KIND_NAME`, Hadoop `Token`, `Text`, and `TokenSelector`.

## Risks and test signals
Tests should cover null service, empty token collections, kind mismatch, service mismatch, first-match behavior, and successful typed return.
