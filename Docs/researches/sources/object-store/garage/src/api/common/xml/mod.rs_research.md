## sources/object-store/garage/src/api/common/xml/mod.rs

Purpose: XML module root and shared XML utility wrappers for S3-compatible config documents.

Important APIs/types/functions: public submodules `cors`, `lifecycle`, `website`; `to_xml_with_header`, `unprettify_xml`, `xmlns_tag`, `xmlns_xsi_tag`, `Value`, and `IntValue`.

Control flow: `to_xml_with_header` prefixes quick-xml serialization with the XML declaration. `unprettify_xml` trims each line for test comparisons. Namespace serializer helpers write S3 XML namespace values. `Value` and `IntValue` wrap element `$value` content and provide `From<&str>` for `Value`.

State/persistence: none.

Dependencies/integration: used by CORS/lifecycle/website XML modules and S3 config handlers.

Risks: pretty/whitespace handling is test-only and not a general XML canonicalizer. Namespace strings are hard-coded to AWS S3 namespaces.

Test signals: no direct tests here, but helper functions are used by XML module round-trip tests.
