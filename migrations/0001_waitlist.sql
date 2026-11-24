-- Beta sign-ups from the landing page form. One row per email; the first entry is kept.
CREATE TABLE IF NOT EXISTS signups (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  email         TEXT NOT NULL UNIQUE,   -- lower-cased
  lang          TEXT NOT NULL,          -- page the form was on: zh-Hans or en
  storage       TEXT NOT NULL,          -- where their saves pile up today, comma separated
  storage_other TEXT NOT NULL,
  sources       TEXT NOT NULL,          -- where they find things to save, comma separated
  sources_other TEXT NOT NULL,
  assistant     TEXT NOT NULL,          -- the AI assistant they use most
  mode          TEXT NOT NULL,          -- own-assistant or built-in-agent
  note          TEXT NOT NULL,          -- what bothers them most about their current tool
  ip_hash       TEXT NOT NULL,          -- SHA-256 of the sender's address, never the address itself
  created_at    TEXT NOT NULL,          -- ISO 8601, UTC
  invited_at    TEXT                    -- filled in by hand when someone is invited
);

-- One row per submission attempt, used only to refuse floods from one address.
CREATE TABLE IF NOT EXISTS attempts (
  ip_hash TEXT NOT NULL,
  at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS attempts_by_ip ON attempts (ip_hash, at);
