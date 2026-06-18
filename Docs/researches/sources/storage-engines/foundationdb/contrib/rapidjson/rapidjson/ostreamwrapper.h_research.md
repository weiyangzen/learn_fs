# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/ostreamwrapper.h

Purpose: `BasicOStreamWrapper` adapts `std::basic_ostream`-derived objects to RapidJSON's output stream concept.

Important APIs and types: `BasicOStreamWrapper<StreamType>` exposes `Ch`, constructor from a stream reference, `Put(Ch)`, and `Flush()`. Typedefs `OStreamWrapper` and `WOStreamWrapper` cover `std::ostream` and `std::wostream`. Input/in-situ methods assert if called.

Control flow: `Put()` forwards one character to `stream_.put(c)`. `Flush()` calls `stream_.flush()`. No buffering is added by the wrapper; buffering remains the responsibility of the underlying stream buffer.

State and persistence behavior: The wrapper stores only a reference to the stream. It does not own, close, or track error state. Persistence is whatever the wrapped stream performs.

Dependencies and integration points: It includes `stream.h` and `<iosfwd>`. `Writer` and `PrettyWriter` can serialize JSON directly to standard streams through this adapter.

Risks: Stream errors are not surfaced through the wrapper API. The not-implemented methods return `char` rather than `Ch`, but they assert and are not intended for use. Copying is disabled because the stream reference is non-owning.

Test signals: Write compact and pretty JSON to `std::ostringstream`, wide output to `std::wostringstream`, explicit flush behavior, and underlying stream failure handling expectations.
