# ai-collab

A small skill for AI coding agents (Claude Code, Codex) that keeps **AI-to-AI handoffs stable**: when the same brief is given to different AIs, they should understand the same words, the same instructions, the same information and start from the same files.

## What it does
- **Four writing rules for a brief**: use the shared glossary for special words; write generic actions instead of one AI's tool names; quote sources with line/uuid and SHA256 instead of paraphrasing; list required files with SHA256 and needed abilities.
- **One receipt line** from the receiving AI before it starts: `收到：<ticket>｜<first 8 chars of each required file's SHA256>｜做不到的動作：無／<list>`. If a fingerprint does not match, it stops.
- **brief_lint.py**: a local, one-second text check of a brief. It only gives reminders; it is not an approval.

No extra AI runs, no extra documents (no read-back, report or status files).

## Files
- `SKILL.md`: the skill (Traditional Chinese)
- `references/terms.json`: shared glossary, one word one meaning
- `references/actions.json`: generic action → how Claude Code / Codex does it
- `scripts/brief_lint.py`: brief checker (`python -B scripts/brief_lint.py <brief>`)

## Install
Copy the `ai-collab` folder into your agent's skills folder (for example `~/.claude/skills/` or `~/.codex/skills/`).

## Works best with 治理系統 Pro
ai-collab only handles how AIs talk to each other. Authorization, scope, independent checks, verdicts, state and handoff are left to **治理系統 Pro (Governance Pro)**, a seven-step governance system for AI work:
https://aquaquest23.gumroad.com/l/governance-pro

## 中文說明
ai-collab 讓 AI 交給 AI 的過程穩定：同一份交辦單交給不同的 AI，文字、指令、資訊和起點的理解都要相同。

用法很簡單：
1. 照四條寫法規則寫交辦單。
2. 對方開工第一句回一行收到確認。
3. 寫完可以用 brief_lint.py 在本機掃一次，結果只是提醒。

授權、範圍、檢查、判定這些事都交給「治理系統 Pro」管。

## Limits
This skill cannot force an AI to follow it. brief_lint.py only checks wording, not meaning.

## License
MIT
