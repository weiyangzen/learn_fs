## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/package-info.java

Purpose: package-level Javadoc for Recon chatbot agent and tool execution classes. It documents that this package owns the agent-facing execution layer rather than REST endpoint or LLM-provider concerns.

Important APIs/types/functions: no runtime API; the only declaration is the `org.apache.hadoop.ozone.recon.chatbot.agent` package.

Control flow and state: none. Integration is documentation-level only, but it groups `ToolExecutor` and adjacent agent classes for Javadoc and package scanning.

Risks and test signals: compile/package-info validation is sufficient. Documentation should remain aligned with actual package responsibilities if future classes move agent planning, tool schema, or execution policy elsewhere.
