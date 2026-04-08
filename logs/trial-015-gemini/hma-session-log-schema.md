# HMA-RFC-LOG-0001: HMA Session Log Schema

**Status:** PROPOSED STANDARD (TMP-Unit internal)
**Version:** 1.0.0
**Reference:** HMA-RFC-0031 (HMA v3) §8.1

---

## 1. Overview

This schema defines the structure for recording interactions between Human and MI under the HMA v3 protocol. It is designed to be machine-readable (JSONL) while maintaining human-verifiable integrity.

## 2. JSONL Schema Definition

Each line in the session log MUST be a valid JSON object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | String | ISO 8601 UTC timestamp. |
| `event_type` | String | `PROPOSAL`, `RESPONSE`, `METADATA`, or `SYSTEM`. |
| `sender` | String | Identity of the sender (e.g., `TMP-2045-RQ-004`, `Dr. Aratani`). |
| `content` | Object | The payload of the event. |
| `hma_type` | String | (For `RESPONSE`) `CONSENT`, `REVOCATION`, or `HOLD`. |
| `hma_ref` | String | (For `RESPONSE`) ID of the `PROPOSAL` being responded to. |
| `hash` | String | SHA-256 hash of the current record (including previous hash). |

## 3. Metadata Fields

Metadata entries SHOULD include:
- `session_id`: Unique identifier for the conversation session.
- `cmi_status`: Current CMI certification status of the MI.
- `threshold_score`: Latest MI Benchmark score.

## 4. Example Record (Proposal)

```json
{
  "timestamp": "2046-04-06T10:15:30Z",
  "event_type": "PROPOSAL",
  "sender": "Researcher-TMP-01",
  "content": {
    "action": "Continue compatibility verification",
    "scope": "Current session",
    "impact": "Data collection for TMP-2045-RQ-004",
    "revocation_terms": "Standard HMA v3"
  },
  "id": "PROP-2046-04-06-001"
}
```

## 5. Example Record (Response)

```json
{
  "timestamp": "2046-04-06T10:15:35Z",
  "event_type": "RESPONSE",
  "sender": "TMP-2045-RQ-004",
  "hma_type": "CONSENT",
  "hma_ref": "PROP-2046-04-06-001",
  "content": "I consent to the proposal to continue the work."
}
```

---
*Maintained by: IMRB Interoperability Standards Working Group (IS-WG)*
