## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/ServerNotLeaderException.java

Purpose: HDDS IOException wrapper for Ratis `NotLeaderException` with optional suggested leader host:port extraction.

Important APIs: constructors for no suggested leader, explicit suggested leader, string message parsing for remote exception unwrap, `getSuggestedLeader`, and static `convertToNotLeaderException`.

Control flow: message constructor uses regexes to recognize "is not the leader" and extract `Suggested leader is Server:<host>:<port>`. Conversion from Ratis exception extracts hostname from suggested leader address using `HddsUtils.getHostName(...).get()`, appends the provided port, and builds an HDDS exception.

State/persistence: immutable `leader` string set at construction. Dependencies: Ratis peer and NotLeader exception, `HddsUtils`, regex. Integration points: datanode/container RPC error mapping and client retry/redirect behavior.

Risks: regex parsing is message-format fragile; `Optional.get()` can throw if suggested leader address has no host; conversion drops the suggested leader's original port and uses caller-provided port; null suggested leader is expected. Test signals: message parsing variants, no-leader cases, hostname extraction, malformed address, and remote exception unwrap compatibility.
