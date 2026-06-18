# sources/storage-engines/foundationdb/contrib/TraceLogHelper/XmlParser.cs

Purpose: streaming parser for XML FoundationDB trace files and summarized TestHarness XML.

Important APIs/functions: `XmlParser.Parse`, private `ParseEvent`, `ParseTestPlan`, `ParseTest`, and `StreamElements`.

Control flow: advances to the `Trace` element, streams child elements, maps `<Event>` to `Event`, `<TestPlan>` to `TestPlan`, and `<Test>` to `Test`; supports sampling, time filtering, rolled event original time, defaulted attributes, original element retention, and nested summarized test events.

State and persistence: read-only stream parser with static `Random`.

Dependencies and integration: System.Xml, LINQ to XML, TraceLogHelper data types.

Risks and test signals: `reader.ReadToDescendant("Trace")` assumes trace wrapper; `bool.Parse` for `OK` is strict while other code often uses `Ok`; nonfatal streaming errors break the parse. Test event, TestPlan, Test, rolled event, time filter, malformed tail, and missing optional attributes.
