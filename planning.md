# TakeMeter - planning.md

---

## Community
I chose the Reddit community r/worldcup, a discussion forum focused on the FIFA World Cup. This community is a good fit for a classification task because users regularly engage in different types of discourse, including tactical analysis, predictions about future matches and tournament outcomes, and emotional reactions to games, players, and refereeing decisions. These distinct forms of discussion are common throughout the community and reflect meaningful differences in how fans participate in conversations about soccer.

---

## Labels

**Analysis:**
A post that explains a soccer-related claim using evidence, tactical reasoning, statistics, historical comparisons, or specific observations.
- Ex: Cristiano Ronaldo breaks 60 year-old record, becomes Portugal's highest goal scorer in FIFA world cup
- Ex: The Argentinian squad actually wants to create chances for Messi because Messi himself leaves his ego in the locker room. Ronaldo, however, makes everything about himself especially on the world stage.

**Prediction:**
A post whose primary purpose is forecasting a future outcome, performance, result, or event involving teams, players, or the tournament.
- Ex: They're probably going to win against us, they're probably going to win the whole tournament
- Ex: Mbappe will finish the tournament as the leading scorer

**Reaction:**
A post that primarily expresses an emotional response, opinion, excitement, dissapointment, or surprise without substantial reasoning or evidence.
- Ex: WHAT A GOAL! That's one of the best goals so far
- Ex: This referee has been terrible all game

---

## Hard Edge Case
The most difficult cases, and probably the most promiminent, will be posts that contain both analysis and prediction.
- Ex: Spain will win the World Cup because they create more chances than any other team and have allowed the fewest shots on target
This post includes analytical evidence to make a prediction about a future outcome in the tournament.

Decision rule: 
- If the primary purpose of the post is explaining why something happened or describing a current situation, it will be labeled as Analysis
- If the primary purpose is forecasting a future outcome, it will be labeld as Prediction.
- Supporting evidence does not automatically make a post Analysis if the main claim is future-oriented

---

## Difficult Cases

**Case 1:**

**Case 2:**

**Case 3:**

---

## Data Collection Plan
I will collect comments and posts from r/worldcup. To avoid collecting only one type of discourse, I will sample from several discussion categories. This will include match threads, tournament discussion threads, and prediction-focused discussions. My target is approximately 70 analysis examples, 65 prediction examples, and 70 reaction examples for a total of 200 examples. 

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
