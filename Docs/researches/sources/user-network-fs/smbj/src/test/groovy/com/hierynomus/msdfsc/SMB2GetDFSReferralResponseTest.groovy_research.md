# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/SMB2GetDFSReferralResponseTest.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/SMB2GetDFSReferralResponseTest.groovy

Purpose: Spock parser tests for DFS referral response wire payloads. Important APIs are `SMB2GetDFSReferralResponse.read(SMBBuffer)`, `referralEntries`, `referralHeaderFlags`, and `DFSReferral.ServerType`. Control flow decodes fixed hex buffers and asserts parsed version, server type, flags, DFS path, alternate path, target path, TTL, special name, and expanded names.

State and persistence: no persisted state; each test constructs a fresh buffer and response object. Dependencies include `SMBBuffer` and DFS referral message classes. Integration points are SMB2 IOCTL DFS referral decoding and resolver inputs. Risks covered include version 3 domain referrals, version 4 root/link referrals, UTF-16 string offsets, null alternate/path fields, and header flags. Test signal is strong for known wire examples but narrow to one-entry responses.
