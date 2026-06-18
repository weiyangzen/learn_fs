# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecProtocolsss.cc

Purpose: implementation of the XRootD `sss` security protocol. It creates encrypted credentials from local or mapped identities on clients and authenticates them on servers using shared keytabs.

Important APIs and functions: implements `Authenticate()`, `getCredentials()`, `Init_Client()`, `Init_Server()`, `Load_Client()`, `Load_Server()`, exported `XrdSecProtocolsssInit()`, and exported `XrdSecProtocolsssObject()`. Private helpers `Decode()`, `Encode()`, `getCred()`, `getLID()`, `Load_Crypto()`, `myClock()`, `setID()`, and `setIP()` manage packets, crypto, and identity buffers. Local `Persona` accumulates decoded identity fields.

Control flow: load-time init chooses keytab and crypto settings. Client object init parses server parameters of the form encryption/lifetime/keytab. `getCredentials()` extracts socket and URL identity hints, obtains serialized identity data from `XrdSecsssID` or static identity, selects a key, fills an SSS record header, and encrypts the data. Server `Authenticate()` validates size and protocol, decrypts via keytab lookup, checks credential age and source host/IP unless disabled by key options, handles mutual-auth login-ID exchange, maps identity and groups based on key options, and populates `XrdSecEntity`.

State and persistence: static process-wide defaults include `ktObject`, `CryptObj`, `idMap`, `staticID`, `aProts`, `deltaTime`, and mode flags. Per-instance state holds endpoint names/IPs, active keytab/crypto references, sequence state, and a reusable identity buffer. Persistent secrets live in keytab files managed by `XrdSecsssKT`.

Dependencies and integration: integrates with the XRootD security plugin ABI, `XrdSecEntity`, `XrdOucErrInfo`, `XrdOucEnv`, `XrdOucPup`, `XrdNetAddrInfo`, `XrdNetUtils`, `XrdCryptoLite`, `XrdSecsssKT`, `XrdSecsssID`, `XrdSecsssEnt`, and RR wire structs. Environment variables include `XrdSecDEBUG`, `XrdSecSSSKT`, and `XrdSecsssKT`.

Risks: security-sensitive parsing uses packed binary data, manual allocation, `alloca`, and static mutable globals guarded only during some init paths. Clock skew causes credential expiry. Host/IP checks can be disabled by key-name convention. V1/V2 buffer limits and key-name padding require exact compatibility tests.

Test signals: round-trip credentials for static, mapped, mutual, and proxied modes; key-name V2 lookup; expired credential rejection; IP mismatch rejection; keytab refresh; malformed packet sizes/types; unsupported crypto; missing keytab; and attribute key/value ordering errors.
