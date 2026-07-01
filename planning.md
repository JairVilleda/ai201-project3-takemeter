# TakeMeter - planning.md

---

## Community
I chose the Reddit community r/worldcup, a discussion forum focused on the FIFA World Cup. This community is a good fit for a classification task because users regularly engage in different types of discourse, including tactical analysis, predictions about future matches and tournament outcomes, and emotional reactions to games, players, and refereeing decisions. These distinct forms of discussion are common throughout the community and reflect meaningful differences in how fans participate in conversations about soccer.

---

## Labels

### Analysis
A post whose primary purpose is **explaining or evaluating a current or past soccer situation** using evidence, tactical reasoning, statistics, historical comparison, specific observations, or causal explanation. Analysis may include brief future implications or recommendations if they are conclusions drawn from the explanation rather than the main point.

- Ex: Cristiano Ronaldo breaks 60-year-old record, becomes Portugal's highest goal scorer in FIFA World Cup history.
- Ex: The Argentinian squad creates chances for Messi because he leaves his ego in the locker room, while Ronaldo often becomes the focal point of the attack.

### Prediction
A post whose primary purpose is **forecasting a future outcome, performance, ranking, result, or event** involving a team, player, match, or the tournament. A prediction remains Prediction even when supported by evidence, tactical reasoning, or historical comparisons.

- Ex: They're probably going to beat us, and they're probably going to win the whole tournament.
- Ex: Mbappé will finish the tournament as the leading scorer.

### Reaction
A post whose primary purpose is **expressing an emotional response, opinion, excitement, disappointment, praise, frustration, surprise, or celebration** without substantial explanatory reasoning. Brief observations or factual statements that support the emotion do not change the label.

- Ex: WHAT A GOAL! That's one of the best goals so far!
- Ex: This referee has been terrible all game.

---

## Hard Edge Cases

Many posts in r/worldcup contain a mix of analysis, prediction, and reaction. The most common ambiguity occurs when a comment includes tactical analysis followed by a prediction, or emotional language followed by analytical reasoning.

### Decision Rules

1. **Primary Communicative Purpose**
   - When a post contains multiple discourse types, classify it according to the author's primary communicative purpose rather than the first sentence or strongest wording.
   - Ask: *If I summarized this comment in one sentence, what is the author ultimately trying to communicate?*

2. **Analysis vs. Prediction**
   - If the main claim is about a future outcome, classify it as Prediction, even if it is supported by tactical reasoning, statistics, or historical evidence.
   - If the main claim is explaining or evaluating a current or past situation, classify it as Analysis, even if it ends with a brief prediction or recommendation.

3. **Forecasts Derived from Analysis**
   - If a future-oriented statement is simply the conclusion of a broader tactical or performance analysis, classify the post as Analysis.

4. **Emotional Framing vs. Emotional Purpose**
   - Do not classify a post as Reaction simply because it begins with emotional language ("Wow," "I'm worried," "I'm proud," etc.).
   - If the majority of the post explains tactics, performance, or strategy, classify it as Analysis.
   - Use Reaction only when expressing emotion or opinion is the primary purpose.

5. **Current Evaluations Require Reasoning**
   - Evaluations of a team's or player's current strength, form, or performance are Analysis only when supported by explanatory reasoning (evidence, tactical detail, statistics, or causal explanation).
   - Bare evaluative opinions ("their defense was solid," "New Zealand is terrible," "we're better in midfield") are Reaction.
   - Purely future evaluations ("they will win," "he'll finish top scorer") are Prediction.

6. **Supporting Evidence Does Not Determine the Label**
   - Evidence, statistics, or historical comparisons do not automatically make a post Analysis.
   - Likewise, emotional language does not automatically make a post Reaction.
   - The supporting content should not override the post's primary communicative purpose.

7. **Recommendations and Advice**
   - Posts recommending tactical or strategic changes ("they need to press higher," "they have to change formations") are Analysis when they explain a current weakness.
   - They become Prediction only when the primary claim is forecasting what will happen rather than explaining what is wrong.

8. **Meta-Soccer Discussion**
   - Discussion about tournament format, qualification, scheduling, or competition structure is classified as Analysis when it explains how those systems affect teams or outcomes.

9. **Records, Milestones, and Historic Achievements**
   - Posts celebrating a goal, record, or milestone with primarily emotional delivery (exclamations, all-caps, praise, excitement) are Reaction, even if they include a statistic.
   - Neutral, factual statements reporting records, milestones, or historic achievements are Analysis.

---

## Difficult Cases

### Case 1
**Text:** "One of the best in the tournament so far. Wouldn't be surprised to see it in the top 10 goals at the end of the tournament."

**Final Label:** Prediction

**Reasoning:** The post begins with a present evaluation, but its primary communicative purpose is forecasting the goal's final standing in the tournament. According to the Analysis vs. Prediction rule, the future-oriented claim determines the label.

---

### Case 2
**Text:** "They were great defensively but only had like 1 shot on target. Ghana cannot win with this defensive structure. They will have to change for the knockout stage, where you cannot just draw."

**Final Label:** Analysis

**Reasoning:** Although the comment ends with a future-oriented recommendation, the majority of the post explains Ghana's current tactical weaknesses. The prediction is a conclusion derived from the analysis rather than the main purpose.

---

### Case 3
**Text:** "FASTEST GOAL JAPAN MADE IN WORLD CUP HISTORY! Japan scores against Tunisia under 6 minutes."

**Final Label:** Reaction

**Reasoning:** This was initially difficult because it contains a factual statistic. However, the primary purpose is celebrating the moment rather than informing or explaining. The emotional delivery (all caps and exclamation) classifies it as Reaction under the records and milestones rule.

---

## Data Collection Plan
I will collect comments and posts from r/worldcup. To avoid collecting only one type of discourse, I will sample from several discussion categories. This will include match threads, tournament discussion threads, and prediction-focused discussions. My target is approximately 70 analysis examples, 65 prediction examples, and 70 reaction examples for a total of 210 examples. 

If prediction examples are underrepresented, I will intentionally collect additional examples from prediction and tournamnet outlook discussions until the label distribution is more balanced. One label should not represent less than 20% of the dataset. I planned ahead by using the r/worldcup community instead of the broader r/soccer commmunity since I would naturally expect more prediction examples in a tournament-focused discussion forum. 

---

## Evaluation Metrics
I will evaluate both the fine-tuned model and the zero-shot Groq baseline using:
- Accuracy
- Precision for each class
- Recall for each class
- F1 score for each class
- Confusion matrix
Accuracy provides an overall measure of performance but can hide weakenesses in individual labels.  Precision and recall help identify whether the model is overpredicting or underpredicting certain classes. F1 score balances precision and recall and is useful if the class distribution is not perfectly balanced. The confusion matrix will show which labels are most frequently confused with one another, which helps identify weaknesses in the taxonomy and model behavior.

---

## Definition of Success
I will consider the project successful if the fine tuned model:
- Achieves at least 75% overall accuracy on the test set
- Achieves an F1 score of at least 0.70 for each label
- Outperforms the zero-shot Groq baseline by at least 5 percentage points in overall accuracy
For a real community moderation or discussion-analysis tool, I would consider performance above 80% accuracy wiht consistent per-class F1 scores above 0.75 to be good enough for practical use, while still requiring human review for ambiguous cases.

---

## AI Tool Plan

**Label stress-testing:**
Before collecting the full dataset, I will provide my label definitions and edge-case rules to ChatGPT and ask it to generate 5–10 borderline examples. If multiple examples cannot be classified confidently, I will revise the label definitions before annotation begins.

**Annotation assistance:**
I will not use an LLM to directly label my final dataset. All labels will be assigned manually to maintain consistency and ensure I fully understand the classification boundaries. However, I may use an LLM to discuss difficult examples during the label-design phase.

**Failure analysis:**
After evaluating the model, I will provide examples of incorrect predictions to Claude and ask it to identify common error patterns. Possible patterns include confusion between Analysis and Prediction, reliance on emotional language, or overemphasis on certain keywords. I will verify any suggested patterns by manually reviewing the misclassified examples before including them in my final report.

**Data collecting worflow:**
I used Claude Code to build the annotation workflow and supporting tools for dataset collection. Specifically, it generated:
- A helper script (add_examples.py) that imports batches of collected r/worldcup posts/comments into worldcup_dataset.csv, automatically formats the data, and prevents duplicate entries.
- A manual annotation tool (annotate.py) that presents one unlabeled example at a time, allows me to assign one of the three predefined labels (Analysis, Prediction, or Reaction), optionally record notes for difficult cases, automatically saves progress after each annotation, supports resuming where I left off, and monitors label distribution throughout the annotation process.
No AI was used to assign labels to the final dataset. Every example was reviewed and labeled manually by me according to the label definitions and decision rules described in this planning document.