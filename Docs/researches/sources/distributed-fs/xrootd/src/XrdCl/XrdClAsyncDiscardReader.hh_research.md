# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncDiscardReader.hh

Purpose: implements a raw reader used when raw data is not expected. Receiving raw bytes in this path is treated as a protocol error.

Important APIs: constructor forwarding URL/request to `AsyncRawReaderIntfc`, `Read(Socket&, uint32_t&)`, and `GetResponse(AnyObject*&)`. `Read` logs the unexpected raw-data condition and returns `errCorruptedHeader`; `GetResponse` returns `errInvalidResponse`.

Control flow/state: it inherits all base reader state but intentionally does not consume or persist data. The control decision is conservative: drop the connection because the stream may be desynchronized. Dependencies are socket/status/logging constants and the raw reader interface. Integration point is stream message handling when an unexpected raw body handler is installed. Risks: behavior is intentionally disruptive but protects protocol framing; tests should assert no silent discard. Test signals: unexpected raw body results in corrupted-header status, response retrieval returns invalid response, and reconnect/retry is triggered by the owning stream.
