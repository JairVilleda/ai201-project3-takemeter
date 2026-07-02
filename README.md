# TakeMeter: r/worldcup Text Classification

A 3-class text classifier for Reddit r/worldcup posts and comments: **Analysis**, **Prediction**, **Reaction**. It compares a zero-shot LLM baseline against a fine-tuned DistilBERT model.

---

## 1. Project Overview
The goal is to automatically sort r/worldcup posts and comments into three types of soccer discourse:

- **Analysis**: explains or evaluates a past/current situation with reasoning
- **Prediction**: forecasts a future outcome
- **Reaction**: expresses emotion or opinion without real reasoning

This matters because the three represent different ways fans participate, which is useful for moderation and for surfacing higher-information posts from the flood of emotional reactions. The task is single-label 3-class classification.

---

## 2. Community Selection
**r/worldcup** is a forum focused on the FIFA World Cup. It was chosen because users regularly post all three discourse types: tactical **analysis**, **predictions** about upcoming matches, and emotional **reactions** to games and calls. Being tournament-focused, it naturally produces more prediction content (match outlooks, brackets) than a broader forum like r/soccer, making it well-suited to a balanced 3-class problem.

---

## 3. Label Taxonomy
### Definitions & Examples

**Analysis**: primary purpose is explaining or evaluating a past/current situation with evidence, tactics, stats, or causal reasoning.
- "Cristiano Ronaldo breaks 60-year-old record, becomes Portugal's highest goal scorer in World Cup history."
- "Argentina creates chances for Messi because he leaves his ego in the locker room, while Ronaldo often becomes the focal point of the attack."

**Prediction**: primary purpose is forecasting a future outcome, result, or event. Stays Prediction even when backed by reasoning.
- "They're probably going to beat us, and win the whole tournament."
- "Mbappé will finish the tournament as the leading scorer."

**Reaction**: primary purpose is expressing emotion, opinion, praise, or frustration without substantial reasoning.
- "WHAT A GOAL! One of the best so far!"
- "This referee has been terrible all game."

### Decision Rules (for mixed posts)
Classify by **primary communicative purpose**, not the first sentence. Key rules:
1. **Analysis vs. Prediction**: a future main claim is Prediction (even if reasoned). A forecast that's just the conclusion of an explanation stays Analysis.
2. **Emotion vs. purpose**: opening with "Wow" doesn't make it Reaction. Use Reaction only when emotion is the point.
3. **Evaluations**: current-form claims are Analysis only if reasoned; bare opinions ("their defense was solid") are Reaction; purely future claims are Prediction.
4. **Records/milestones**: celebratory delivery (all-caps, exclamations) is Reaction even with a stat; neutral factual reporting is Analysis.

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

All classes stay above the 20% floor. The plan targeted a balanced ~70/65/70; Prediction ended up smallest at 27.2%.

### Difficult-to-Label Cases
1. **"One of the best so far. Wouldn't be surprised to see it in the top 10 goals at the end of the tournament."** → **Prediction.** Opens with an evaluation, but the main point forecasts the goal's final ranking.
2. **"They were great defensively but only had 1 shot on target. Ghana can't win with this structure. They'll have to change for the knockouts."** → **Analysis.** Ends with a forecast, but mostly explains a current weakness; the forecast is a conclusion.
3. **"FASTEST GOAL JAPAN MADE IN WORLD CUP HISTORY! Under 6 minutes vs Tunisia."** → **Reaction.** Has a stat, but the all-caps celebration is the purpose (records/milestones rule).

---

## 5. Baseline Model (Zero-Shot LLM)
- **Model:** Groq `llama-3.3-70b-versatile` (`temperature=0`, `max_tokens=20`).
- **Prompt:** one `SYSTEM_PROMPT` with the task, the three definitions, one example per label, tie-breaking rules, and an instruction to output only the label name (full text below). Each post is sent as the user message `"Classify this post:\n\n{text}"`.
- **Collection:** `classify_with_groq(text)` calls the API; output is stripped and matched case-insensitively to a label, else `None`. **31/31 (100%)** responses were parseable.

<details>
<summary>Full <code>SYSTEM_PROMPT</code></summary>

```
You are classifying Reddit posts from the r/worldcup community.
Your task is to assign each post exactly one label.

Labels:

Analysis:
A post whose primary purpose is explaining or evaluating a current or past soccer
situation using tactical reasoning, statistics, historical comparisons, specific
observations, or causal explanation.
Example: Ghana cannot win with this defensive structure. They will have to change
for the knockout stage.

Prediction:
A post whose primary purpose is forecasting a future outcome, performance, result,
or event involving teams, players, or the tournament. This includes predictions
even if supported by evidence or reasoning.
Example: Mbappé will finish as the top scorer in the tournament.

Reaction:
A post whose primary purpose is expressing emotion, excitement, disappointment,
praise, frustration, or surprise without substantial explanatory reasoning.
Example: WHAT A GOAL! This match is unbelievable!

IMPORTANT RULES:
- Choose ONLY ONE label.
- If the post is about the future outcome → Prediction.
- If the post explains a current or past situation → Analysis.
- If the post is mainly emotional or opinionated without reasoning → Reaction.
- Do NOT explain your answer.
- Output ONLY one word exactly: Analysis | Prediction | Reaction
```
</details>

### Results: 61.3% accuracy

| Class | Precision | Recall | F1 |
|-------|-----------|--------|------|
| Analysis   | 0.58 | 0.58 | 0.58 |
| Prediction | 0.75 | 0.67 | 0.71 |
| Reaction   | 0.55 | 0.60 | 0.57 |

Best on Prediction (future-oriented language is easy for a large LLM); weakest on Analysis/Reaction, which it sometimes confuses since many posts mix reasoning and emotion.

---

## 6. Fine-Tuning Approach
- **Base model:** `distilbert-base-uncased` (`AutoModelForSequenceClassification`, `num_labels=3`).
- **Data:** 202 examples, stratified **70/15/15** split into **~141 train / ~30 val / 31 test**.
- **Tokenization:** `AutoTokenizer`, `truncation=True`, `max_length=256`, `DataCollatorWithPadding`.
- **Training:** HuggingFace `Trainer`, evaluating each epoch (`eval_strategy="epoch"`) and keeping the **best checkpoint by validation accuracy** (`load_best_model_at_end=True`). Predictions come from a softmax over the logits (also gives the confidence score).

### Hyperparameters
Learning rate `2e-5`, `3` epochs, batch size `16`, `weight_decay=0.01`, `warmup_steps=50`, max length `256`. These are the standard DistilBERT fine-tuning defaults, each chosen for a small dataset:

- **Learning rate `2e-5`:** the standard BERT-family starting point, low enough to avoid wiping the pretrained weights.
- **3 epochs:** few passes limit overfitting on ~141 training examples; more epochs would memorize the set.
- **Batch size `16`:** fits a T4 GPU comfortably (drop to 8 on OOM).
- **`warmup_steps=50` + `weight_decay=0.01`:** ramp the LR in gently and regularize, both standard stabilizers for small-data fine-tuning.
- **Max length `256`:** covers Reddit-length posts without wasting compute on padding.

Best checkpoint is selected on validation accuracy, so the reported model is the best of the 3 epochs rather than the last.

---

## 7. Evaluation Results

### Fine-Tuned Model: 45.2% accuracy (14/31)

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|------|---------|
| Analysis   | 0.43 | 1.00 | 0.60 | 12 |
| Prediction | 0.00 | 0.00 | 0.00 | 9 |
| Reaction   | 0.67 | 0.20 | 0.31 | 10 |

### Baseline vs. Fine-Tuned

| Metric | Baseline (Groq) | Fine-Tuned (DistilBERT) |
|--------|-----------------|--------------------------|
| Accuracy | **61.3%** | 45.2% |
| Analysis F1   | 0.58 | 0.60 |
| Prediction F1 | 0.71 | 0.00 |
| Reaction F1   | 0.57 | 0.31 |

**Summary:** the fine-tuned model **regressed by ~16 points**. With only ~141 training examples, it collapsed toward the majority class, predicting Analysis for 28/31 posts and **never predicting Prediction** (F1 = 0.00). The 70B zero-shot LLM already understood all three classes without training. **None** of the planning.md success targets (≥75% accuracy, ≥0.70 F1 per class, +5 pts over baseline) were met; for this dataset size the baseline is the stronger classifier.

---

## 8. Confusion Matrix: Fine-Tuned Model
Rows = true, columns = predicted. (See also `confusion_matrix.png`.)

| True \ Pred | Analysis | Prediction | Reaction | Total |
|-------------|----------|------------|----------|-------|
| Analysis    | 12 | 0 | 0 | 12 |
| Prediction  | 8  | 0 | 1 | 9  |
| Reaction    | 8  | 0 | 2 | 10 |
| **Total**   | 28 | 0 | 3 | 31 |

The Prediction column is entirely zero, so the model never predicts it. Almost everything is pulled into Analysis: 8/9 Prediction posts and 8/10 Reaction posts, so Analysis gets perfect recall (1.00) but poor precision (0.43). Only 3 posts are predicted Reaction, and Prediction is never assigned.

---

## 9. Error Analysis (Fine-Tuned Model)

### 9.1 Error Patterns (AI-assisted, then verified)
I pasted the confusion matrix and misclassified posts into an LLM to surface error themes, then checked each against the matrix:

- **Prediction is never produced:** verified (column = 0); true Predictions go 8 to Analysis, 1 to Reaction.
- **Reaction absorbed into Analysis:** verified (8/10 Reactions predicted Analysis).
- **Overall collapse toward Analysis:** verified (28/31 predicted Analysis).
- **Near-chance confidence:** all 17 wrong predictions scored 0.35–0.40, barely above the 0.33 chance floor. The model isn't confidently wrong; it's essentially guessing.

**Verification note:** the LLM called this a "Prediction to Analysis collapse." I checked it against the matrix and it **held**. 8 of 9 Predictions land in Analysis (the 9th in Reaction), so the collapse is real and the Prediction label is never assigned at all.

### 9.2 Misclassified Examples

**1. "Colombia gonna go 1st in group K"** (true **Prediction**, predicted **Analysis**, 0.36)
A casual forecast with no explicit "will" that names a team and standing, so it reads as descriptive. **Data problem, not labeling:** Prediction was the smallest class with few informal forecasts. *Fix:* more casual, low-modal Prediction examples.

**2. "Korea winning the wc"** (true **Prediction**, predicted **Analysis**, 0.35)
Four words, no reasoning, almost no signal, and with Prediction never assigned it defaults to the majority class. **Post-length/data problem.** *Fix:* more short Prediction examples; ultra-short posts may stay ambiguous without context.

**3. "Unbelievable match!! Two GREAT Team"** (true **Reaction**, predicted **Analysis**, 0.35)
All-caps and exclamations make this a textbook Reaction, yet the model still chose Analysis at chance confidence. **Model/data problem:** the Analysis majority bias overrides even strong emotional cues. *Fix:* more Reaction examples and/or class rebalancing.

---

## 10. Sample Classifications (Fine-Tuned Model)

| # | Text | Predicted | Confidence | Correct? |
|---|------|-----------|------------|----------|
| 1 | "Tunisia had completely lost the will to fight after conceding the third goal." | Analysis | 0.42 | ✓ (true: Analysis) |
| 2 | "Whatta match it was!!" | Reaction | 0.35 | ✓ (true: Reaction) |
| 3 | "Colombia gonna go 1st in group K" | Analysis | 0.36 | ✗ (true: Prediction) |
| 4 | "Unbelievable match!! Two GREAT Team" | Analysis | 0.35 | ✗ (true: Reaction) |
| 5 | "I have a feeling that Cape Verde will beat Saudi Arabia and move to the next stage." | Analysis | 0.38 | ✗ (true: Prediction) |

**Correct example (row 1):** "Tunisia had completely lost the will to fight after conceding the third goal" is a past-tense, causal evaluation of what happened in a match. This is the explanatory structure the model learned to map to Analysis, so it lands right at its highest confidence (0.42).

The rest illustrate the collapse: row 2 is the rare Reaction the model gets (only 3/31), while the three misses (rows 3–5), two forecasts and one all-caps Reaction, all get swept into Analysis because Prediction is never assigned. Confidences stay low across the board (0.35–0.42, vs a 0.33 floor); even the correct predictions barely clear chance, so the model is never really committing.

---

## 11. Reflection: Intended vs. Learned Behavior
The taxonomy is defined by **intent** (Analysis explains, Prediction forecasts, Reaction emotes). The model learned something shallower, a **surface heuristic**: default to Analysis, with only the most overtly emotional posts occasionally tipping to Reaction (just 3/31). Prediction (about a claim's *direction in time*, not its vocabulary) was never captured.

- **Learned well:** structured, descriptive commentary (Analysis recall = 1.00).
- **Overfit to:** the "informational structure = Analysis" cue and the majority class; with ~141 examples, defaulting to Analysis was the cheapest way to cut loss.
- **Missed:** forecasting intent (Prediction collapsed) and emotion-vs-evaluation (8/10 Reactions read as Analysis); short posts were hardest.

I intended a 3-way *intent* classifier but got a 2-way *register* classifier (informational vs. emotional) with no room for Prediction.

---

## 12. Spec Reflection
Where the `planning.md` spec helped and where reality diverged from it:

**Helped:**
- **Decision rules** kept annotation consistent on the hard boundaries (Analysis-vs-Prediction forecasts, Reaction-vs-Analysis emotion) that would otherwise have been labeled by gut feel. The three difficult cases (§4) were resolved directly by the rules I wrote in advance.
- **The 20% floor guardrail** forced a course-correction: when Prediction lagged, the pre-committed minimum sent me back to prediction threads to top it up, so the class stayed usable (27.2%) rather than degenerating.
- **Pre-committing to manual annotation and to verifying AI patterns** kept the process honest. Because the spec said "no LLM labels" and "check every suggested error pattern," I verified the LLM's "Prediction to Analysis collapse" claim against the matrix before using it (it held, 8/9) rather than copying it in unchecked (§9.1).

**Diverged:**
- **Class balance:** the plan targeted ~70/65/70, but Prediction came in smallest at 27.2% (55 examples). Even sampling prediction-focused threads didn't fully close the gap, and that imbalance plus the small dataset likely drove the model to never learn Prediction (F1 = 0.00).
- **Success criteria:** none of the three targets (≥75% accuracy, ≥0.70 F1 per class, +5 pts over baseline) were met. The fine-tuned model landed at 45.2% and regressed ~16 pts. In hindsight those bars assumed fine-tuning would beat a 70B zero-shot model, which ~141 examples were never going to support.
- **Hypothesis was wrong:** I expected fine-tuning to *sharpen* the Analysis-vs-Reaction and mixed-Prediction boundaries. Instead the model collapsed toward the majority class, the opposite of the improvement I planned for.

---

## 13. AI Usage Disclosure

**1. Tooling (Claude Code).** Directed it to build the data/annotation tools. It produced `add_examples.py` (batch import, formatting, dedup) and `annotate.py` (one-at-a-time manual labeling with notes, auto-save, resume, and live distribution tracking). It wrote the scripts; it never assigned a label.

**2. Label stress-testing (LLM).** Gave it the definitions and edge cases and asked for borderline examples (reasoned forecasts, emotion-vs-tactics, record announcements). Where an example was hard to classify confidently, I revised the definitions, which is what tightened the rules around primary intent and forecasts embedded in analysis.

**3. Failure analysis (LLM).** Pasted the confusion matrix and misclassified posts in and asked for common error patterns. I **verified every suggested pattern against the matrix** before using it (e.g. the "Prediction to Analysis collapse" claim held, since 8 of 9 Predictions land in Analysis) rather than reporting the LLM's themes unchecked.

**4. Annotation (explicitly *not* AI).** No LLM labeled the final dataset. All 202 examples were labeled by hand in `annotate.py` per the definitions and decision rules, so I fully owned the classification boundaries. AI touched tooling, label design, and error analysis but never the labels themselves.

---
