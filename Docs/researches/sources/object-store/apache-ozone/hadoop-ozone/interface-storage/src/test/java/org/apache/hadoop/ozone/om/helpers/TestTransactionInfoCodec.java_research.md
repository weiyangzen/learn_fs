# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestTransactionInfoCodec.java

Purpose: Unit test for `TransactionInfo.getCodec()` persisted-format behavior.

Important APIs/types/functions: Extends `Proto2CodecTestBase<TransactionInfo>`, returns `TransactionInfo.getCodec()`. Tests round trip for `TransactionInfo.valueOf(11, 100)` and overrides malformed-buffer test.

Control flow, state, and persistence: Serializes transaction term/index-like data, deserializes it, and checks equality. Invalid UTF-8 bytes are expected to throw `IllegalArgumentException` containing `Unexpected split length`.

Dependencies and integration points: Uses HDDS `TransactionInfo`, codec base, AssertJ, and JUnit. Transaction info is central for OM DB transaction tracking/checkpoint/replay state.

Risks: Invalid-data assertion is tied to a specific parsing message. Only one positive value pair is tested.

Test signals: Direct positive and negative codec coverage for persisted transaction info.
