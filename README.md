# TakeMeter — r/worldcup Text Classification

A 3-class text classifier for Reddit r/worldcup posts: **Analysis**, **Prediction**, **Reaction**. It compares a zero-shot LLM baseline against a fine-tuned DistilBERT model.

---

## 1. Project Overview
The goal is to automatically sort r/worldcup posts and comments into three types of soccer discourse:

- **Analysis** — explains or evaluates a past/current situation with reasoning
- **Prediction** — forecasts a future outcome
- **Reaction** — expresses emotion or opinion without real reasoning

This matters because the three represent different ways fans participate, which is useful for moderation and for surfacing higher-information posts from the flood of emotional reactions. The task is single-label 3-class classification.

---

## 2. Community Selection
**r/worldcup** — a forum focused on the FIFA World Cup. It was chosen because users regularly post all three discourse types: tactical **analysis**, **predictions** about upcoming matches, and emotional **reactions** to games and calls. Being tournament-focused, it naturally produces more prediction content (match outlooks, brackets) than a broader forum like r/soccer, making it well-suited to a balanced 3-class problem.

---

## 3. Label Taxonomy
### Definitions & Examples

**Analysis** — primary purpose is explaining or evaluating a past/current situation with evidence, tactics, stats, or causal reasoning.
- "Cristiano Ronaldo breaks 60-year-old record, becomes Portugal's highest goal scorer in World Cup history."
- "Argentina creates chances for Messi because he leaves his ego in the locker room, while Ronaldo often becomes the focal point of the attack."

**Prediction** — primary purpose is forecasting a future outcome, result, or event. Stays Prediction even when backed by reasoning.
- "They're probably going to beat us, and win the whole tournament."
- "Mbappé will finish the tournament as the leading scorer."

**Reaction** — primary purpose is expressing emotion, opinion, praise, or frustration without substantial reasoning.
- "WHAT A GOAL! One of the best so far!"
- "This referee has been terrible all game."

### Decision Rules (for mixed posts)
Classify by **primary communicative purpose**, not the first sentence. Key rules:
1. **Analysis vs. Prediction** — a future main claim is Prediction (even if reasoned); a forecast that's just the conclusion of an explanation stays Analysis.
2. **Emotion vs. purpose** — opening with "Wow" doesn't make it Reaction; use Reaction only when emotion is the point.
3. **Evaluations** — current-form claims are Analysis only if reasoned; bare opinions ("their defense was solid") are Reaction; purely future claims are Prediction.
4. **Records/milestones** — celebratory delivery (all-caps, exclamations) is Reaction even with a stat; neutral factual reporting is Analysis.

*(Full rule set in `planning.md`.)*

---

## 4. Data Collection & Annotation
- **Source:** r/worldcup posts/comments, sampled across match threads, tournament threads, and prediction discussions to avoid over-representing one type.
- **Collection:** `add_examples.py` imports batches into `worldcup_dataset.csv`, formats them, and blocks duplicates.
- **Annotation:** all labels assigned **manually** with `annotate.py` (one post at a time, notes, auto-save, resume, live distribution tracking). **No LLM labeled the final dataset.**

### Label Distribution

| Label | Count | Percentage |
|-------|-------|------------|
| Analysis   | 80  | 39.6% |
| Reaction   | 67  | 33.2% |
| Prediction | 55  | 27.2% |
| **Total**  | 202 | 100% |

All classes stay above the 20% floor. The plan targeted a balanced ~70/65/70; Prediction ended up smallest at 27.2% (see §12).

### Difficult-to-Label Cases
1. **"One of the best so far. Wouldn't be surprised to see it in the top 10 goals at the end of the tournament."** → **Prediction.** Opens with an evaluation, but the main point forecasts the goal's final ranking.
2. **"They were great defensively but only had 1 shot on target. Ghana can't win with this structure. They'll have to change for the knockouts."** → **Analysis.** Ends with a forecast, but mostly explains a current weakness; the forecast is a conclusion.
3. **"FASTEST GOAL JAPAN MADE IN WORLD CUP HISTORY! Under 6 minutes vs Tunisia."** → **Reaction.** Has a stat, but the all-caps celebration is the purpose (records/milestones rule).

---

## 5. Baseline Model (Zero-Shot LLM)
- **Model:** Groq `llama-3.3-70b-versatile` (`temperature=0`, `max_tokens=20`).
- **Prompt:** one `SYSTEM_PROMPT` with the task, the three definitions, one example per label, and an instruction to output only the label name. Each post is sent as `"Classify this post:\n\n{text}"`.
- **Collection:** `classify_with_groq(text)` calls the API; output is stripped and matched case-insensitively to a label, else `None`. **31/31 (100%)** responses were parseable.

### Results — 61.3% accuracy

| Class | Precision | Recall | F1 |
|-------|-----------|--------|------|
| Analysis   | 0.58 | 0.58 | 0.58 |
| Prediction | 0.75 | 0.67 | 0.71 |
| Reaction   | 0.55 | 0.60 | 0.57 |

Best on Prediction (future-oriented language is easy for a large LLM); weakest on Analysis/Reaction, which it sometimes confuses since many posts mix reasoning and emotion.

---

## 6. Fine-Tuning Approach
- **Base model:** `distilbert-base-uncased` (`AutoModelForSequenceClassification`, `num_labels=3`).
- **Data:** 202 examples, stratified **70/15/15** split → **~141 train / ~30 val / 31 test**.
- **Tokenization:** `AutoTokenizer`, `truncation=True`, `max_length=256`, `DataCollatorWithPadding`.
- **Training:** HuggingFace `Trainer`. Predictions come from a softmax over the logits (also gives the confidence score).

### Hyperparameters
Learning rate `2e-5`, `3` epochs, batch size `16`, max length `256` — the standard DistilBERT fine-tuning defaults: a low LR avoids wiping the pretrained weights, few epochs limit overfitting on a small dataset, and 256 tokens covers Reddit-length posts.

---

## 7. Evaluation Results

### Fine-Tuned Model — 45.2% accuracy (14/31)

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|------|---------|
| Analysis   | 0.50 | 1.00 | 0.67 | 12 |
| Prediction | 0.00 | 0.00 | 0.00 | 9 |
| Reaction   | 0.29 | 0.20 | 0.24 | 10 |

### Baseline vs. Fine-Tuned

| Metric | Baseline (Groq) | Fine-Tuned (DistilBERT) |
|--------|-----------------|--------------------------|
| Accuracy | **61.3%** | 45.2% |
| Analysis F1   | 0.58 | 0.67 |
| Prediction F1 | 0.71 | 0.00 |
| Reaction F1   | 0.57 | 0.24 |

**Summary:** the fine-tuned model **regressed by ~16 points**. With only ~141 training examples, it collapsed toward the majority class — predicting Analysis for 24/31 posts and **never predicting Prediction** (F1 = 0.00). The 70B zero-shot LLM already understood all three classes without training. **None** of the planning.md success targets (≥75% accuracy, ≥0.70 F1 per class, +5 pts over baseline) were met; for this dataset size the baseline is the stronger classifier.

---

## 8. Confusion Matrix — Fine-Tuned Model
Rows = true, columns = predicted. (See also `confusion_matrix.png`.)

| True \ Pred | Analysis | Prediction | Reaction | Total |
|-------------|----------|------------|----------|-------|
| Analysis    | 12 | 0 | 0 | 12 |
| Prediction  | 4  | 0 | 5 | 9  |
| Reaction    | 8  | 0 | 2 | 10 |
| **Total**   | 24 | 0 | 7 | 31 |

The Prediction column is entirely zero — the model never predicts it. Most Reaction posts (8/10) and several Prediction posts (4/9) are pulled into Analysis, which gets perfect recall (1.00) but poor precision (0.50).

---

## 9. Error Analysis (Fine-Tuned Model)

### 9.1 Error Patterns (AI-assisted, then verified)
I pasted the confusion matrix and misclassified posts into an LLM to surface error themes, then checked each against the matrix:

- **Prediction is never produced** — verified (column = 0); true Predictions split 4→Analysis, 5→Reaction.
- **Reaction absorbed into Analysis** — verified (8/10 Reactions → Analysis).
- **Overall collapse toward Analysis** — verified (24/31 predicted Analysis).
- **Near-chance confidence** — all 17 wrong predictions scored 0.34–0.38, barely above the 0.33 chance floor. The model isn't confidently wrong; it's essentially guessing.

**Corrected:** the LLM called this a "Prediction → Analysis collapse." The matrix shows Predictions actually go slightly more to Reaction (5) than Analysis (4), so the accurate claim is that **the Prediction label is never assigned at all** — I discarded the directional wording.

### 9.2 Misclassified Examples

**1. "Colombia gonna go 1st in group K"** — true **Prediction**, predicted **Analysis** (0.35)
A casual forecast with no explicit "will" that names a team and standing, so it reads as descriptive. **Data problem, not labeling:** Prediction was the smallest class with few informal forecasts. *Fix:* more casual, low-modal Prediction examples.

**2. "Korea winning the wc"** — true **Prediction**, predicted **Reaction** (0.37)
Four words, no reasoning, almost no signal, so the model guesses. **Post-length/data problem.** *Fix:* more short Prediction examples; ultra-short posts may stay ambiguous without context.

**3. "Unbelievable match!! Two GREAT Team"** — true **Reaction**, predicted **Analysis** (0.34)
All-caps and exclamations make this a textbook Reaction, yet the model still chose Analysis at chance confidence. **Model/data problem:** the Analysis majority bias overrides even strong emotional cues. *Fix:* more Reaction examples and/or class rebalancing.

---

## 10. Sample Classifications (Fine-Tuned Model)
Five posts run through the fine-tuned model:

| # | Text | Predicted | Confidence | Correct? |
|---|------|-----------|------------|----------|
| 1 | "Colombia gonna go 1st in group K" | Analysis | 0.35 | ✗ (true: Prediction) |
| 2 | "Korea winning the wc" | Reaction | 0.37 | ✗ (true: Prediction) |
| 3 | "Unbelievable match!! Two GREAT Team" | Analysis | 0.34 | ✗ (true: Reaction) |
| 4 | "Good Luck against Argentina (you're gonna need it)." | Reaction | 0.36 | ✗ (true: Prediction) |
| 5 | "I have a feeling that Cape Verde will beat Saudi Arabia." | Reaction | 0.35 | ✗ (true: Prediction) |

Confidences are uniformly low (0.34–0.37, vs a 0.33 floor) — the model never commits, mirroring the collapsed boundary.

**Why a correct prediction is reasonable:** The model correctly classified **all 12 true-Analysis posts** in the test set (Analysis recall = 1.00). These predictions are reasonable because genuine Analysis posts carry exactly the explanatory, tactical, reasoning-heavy structure the model over-learned as its "Analysis" signal — so when a post really does explain or evaluate a situation, the model's bias lines up with the correct label. _(Add one specific true-Analysis→Analysis post + its confidence from the notebook to anchor this.)_

---

## 11. Reflection — Intended vs. Learned Behavior
The taxonomy is defined by **intent** (Analysis explains, Prediction forecasts, Reaction emotes). The model learned something shallower — a **surface heuristic**: explanatory-looking text → Analysis, otherwise lean Reaction. Prediction (about a claim's *direction in time*, not its vocabulary) was never captured.

- **Learned well:** structured, descriptive commentary (Analysis recall = 1.00).
- **Overfit to:** the "informational structure = Analysis" cue and the majority class; with ~141 examples, defaulting to Analysis was the cheapest way to cut loss.
- **Missed:** forecasting intent (Prediction collapsed) and emotion-vs-evaluation (8/10 Reactions read as Analysis); short posts were hardest.

**In one line:** I intended a 3-way *intent* classifier but got a 2-way *register* classifier (informational vs. emotional) with no room for Prediction.

---

## 12. Spec Reflection
- **Helped:** the decision rules in `planning.md` kept annotation consistent on the hard boundaries (Analysis-vs-Prediction forecasts, Reaction-vs-Analysis emotion), which would otherwise have been labeled inconsistently.
- **Diverged:** the plan targeted a balanced ~70/65/70, but Prediction came in smallest at 27.2% (55 examples). That imbalance plus the small dataset likely caused the model to never learn Prediction (F1 = 0.00).

---

## 13. AI Usage Disclosure
**Instance 1 — Tooling (Claude Code).** Directed it to build the data/annotation tools. It produced `add_examples.py` (batch import, formatting, dedup) and `annotate.py` (manual labeling with auto-save/resume/distribution tracking). *Changed/overrode:* _[note any edits you made]._ No labels were auto-assigned.

**Instance 2 — Label stress-testing (LLM).** Gave it the definitions and edge cases and asked for borderline examples (reasoned forecasts, emotion-vs-tactics, record announcements). Used them to tighten the rules around primary intent and forecasts embedded in analysis.

**Annotation:** no LLM labeled the final dataset — all 202 examples were labeled by hand in `annotate.py`. AI was used only for tooling and label design.

---