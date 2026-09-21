---
name: "hafiza-guncelle"
description: "Oturumda öğrenilenleri kalıcı hafızaya işler: yeni tercihler, proje bilgileri, kısaltmalar, kararlar. \"Bunu hatırla\", \"hafızaya ekle\", \"bunu not al\", \"bir daha sormana gerek kalmasın\" dendiğinde veya uzun bir oturumun sonunda kullan. Also triggers on \"remember this\", \"add this to memory\", \"save this so I don't have to repeat it\", \"note that down for next time\". Tek seferlik görev detayı, geçici durum veya şifre ve API anahtarı gibi hassas veri için kullanma."
---

# Updating memory

The point: never having to explain the same thing twice.

## What goes in, what does not

**Goes in** (things that will be true again):
- Durable preferences ("always deliver reports as PDF", "never use emoji")
- A project's name, purpose, stack, and status
- People and their roles
- Abbreviations, code names, in-house jargon
- Decisions taken, and why
- Recurring workflows
- Corrections ("do not do X again, because Y")

**Does not go in:** one-off task detail, anything already written in a file (link
to it instead), transient state, and **guesses** (if you are not sure, ask; do
not invent and write it down).

## Steps

1. **Read the existing memory** (`CLAUDE.md`, if there is one) so nothing is
   written twice.
2. **Scan the session for:** the moments the user corrected you (a preference
   signal), sentences like "always / never again / we usually / here we do it
   this way", any name, abbreviation or project they explained that is not
   recorded, and the decisions taken.
3. **Propose, then write:**
   ```
   ## Proposed additions
   § Section → "the line to add"   [why: you said this in the session]
   ## Proposed updates
   § Section → old: "..." → new: "..."
   ```
   Get approval, then apply.
4. **Put it in the right place.** Write into the correct section; do not disturb
   the existing structure.
5. **Prune.** Once the file passes 200 lines: delete lines that are no longer
   true, merge duplicates, and move bloated detail into a separate file with a
   link. Show what you are removing before removing it.

## Rules
- **Keep it short.** Memory is read every session; if it bloats, it becomes
  expensive and ineffective at the same time.
- Write what can be checked: "reports as PDF" ✅ / "the user likes tidiness" ❌
- **Never** write sensitive data (passwords, API keys, ID numbers, bank details).
- **Quote the heredoc delimiter.** Memory prose carries backticked code spans
  and dollar signs; an unquoted `<<EOF` runs the backticks as commands and
  writes the file with the span replaced by empty output while reporting
  success. Write through `<<'EOF'` and pass any variable the script needs
  through the environment or a placeholder replaced afterwards.
- Date every entry added to the decision log.

If there is no memory file: ask where it should live, then create it.
